"""Recoverable lab payment, inventory and fulfillment state machine.

Payments and shipments are deterministic simulations. Inventory and its order
checkpoint are committed in the same DynamoDB transaction. The single inventory
catalog is intentionally a lab design, not a production warehouse schema.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Callable
from typing import Any

from boto3.dynamodb.conditions import Attr

from orders.consumer.errors import TransientProcessingError
from orders.consumer.repository import DynamoDBOrderRepository
from orders.shared.tracing import span


class DynamoDBOrderProcessor(DynamoDBOrderRepository):
    """Advance durable orders without repeating reservations after a crash."""

    def __init__(
        self,
        table_name: str,
        *,
        dynamodb_resource: Any | None = None,
        approve_payment: Callable[[dict[str, Any]], bool] = lambda order: True,
        fulfill: Callable[[dict[str, Any]], str] | None = None,
        key_schema: str = "composite",
    ) -> None:
        super().__init__(table_name, dynamodb_resource=dynamodb_resource, key_schema=key_schema)
        self.approve_payment = approve_payment
        self.fulfill = fulfill or (
            lambda order: "sim-shipment-" + hashlib.sha256(order["order_id"].encode()).hexdigest()
        )

    def _read(self, order_id: str) -> dict[str, Any]:
        item = self.table.get_item(Key=self._key(order_id), ConsistentRead=True).get("Item")
        if item is None:
            raise TransientProcessingError("Order checkpoint is absent")
        return item

    def _transition(self, order_id: str, expected: str, target: str, **fields: str) -> None:
        names = {"#state": "status"}
        values: dict[str, Any] = {":target": target}
        updates = ["#state = :target"]
        for index, (key, value) in enumerate(fields.items()):
            names[f"#f{index}"] = key
            # Attr condition builders reserve :v0, :v1, ... themselves.
            values[f":field_{index}"] = value
            updates.append(f"#f{index} = :field_{index}")
        try:
            self.table.update_item(
                Key=self._key(order_id),
                UpdateExpression="SET " + ", ".join(updates),
                ConditionExpression=Attr("status").eq(expected),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
            )
        except self.table.meta.client.exceptions.ConditionalCheckFailedException:
            # A concurrent delivery may have advanced the same checkpoint.
            if self._read(order_id)["status"] == expected:
                raise TransientProcessingError("Checkpoint update conflicted") from None

    def _reserve(self, order: dict[str, Any]) -> None:
        inventory_key = (
            {"order_id": "INVENTORY#LAB"} if self.key_schema == "legacy"
            else {"pk": "INVENTORY#LAB", "sk": "CATALOG"}
        )
        if "Item" not in self.table.get_item(Key=inventory_key, ConsistentRead=True):
            raise TransientProcessingError("Inventory catalog is not configured")
        quantities: Counter[str] = Counter()
        for item in order["items"]:
            quantities[item["sku"]] += int(item["quantity"])
        names = {"#stock": "stock"}
        values: dict[str, int] = {}
        updates, conditions = [], []
        for index, (sku, quantity) in enumerate(sorted(quantities.items())):
            names[f"#sku{index}"] = sku
            values[f":q{index}"] = quantity
            path = f"#stock.#sku{index}"
            updates.append(f"{path} = {path} - :q{index}")
            conditions.append(f"attribute_exists({path}) AND {path} >= :q{index}")
        client = self.table.meta.client
        try:
            # Transaction APIs do not accept Attr builders. Attribute-name tokens
            # keep arbitrary SKUs out of the expression syntax.
            client.transact_write_items(TransactItems=[
                {"Update": {
                    "TableName": self.table.name,
                    "Key": inventory_key,
                    "UpdateExpression": "SET " + ", ".join(updates),
                    "ConditionExpression": " AND ".join(conditions),
                    "ExpressionAttributeNames": names,
                    "ExpressionAttributeValues": values,
                }},
                {"Update": {
                    "TableName": self.table.name,
                    "Key": self._key(order["order_id"]),
                    "UpdateExpression": "SET #state = :reserved",
                    "ConditionExpression": "#state = :paid",
                    "ExpressionAttributeNames": {"#state": "status"},
                    "ExpressionAttributeValues": {":paid": "PAID", ":reserved": "RESERVED"},
                }},
            ])
        except client.exceptions.TransactionCanceledException as error:
            codes = {reason.get("Code") for reason in error.response.get("CancellationReasons", [])}
            if codes - {"None", "ConditionalCheckFailed", None}:
                raise TransientProcessingError("Inventory transaction must be retried") from error
            if self._read(order["order_id"])["status"] != "PAID":
                return
            stock = self.table.get_item(
                Key=inventory_key, ConsistentRead=True,
            ).get("Item", {}).get("stock", {})
            if any(stock.get(sku, 0) < quantity for sku, quantity in quantities.items()):
                # Reservation was atomic: no SKU was decremented. Refund is a
                # simulation checkpoint, not a call to a real payment provider.
                self._transition(order["order_id"], "PAID", "REJECTED",
                                 rejection_reason="OUT_OF_STOCK", payment_status="SIMULATED_REFUNDED")
                return
            raise TransientProcessingError("Inventory contention must be retried") from error

    def persist(self, order: dict[str, Any], created_at: str) -> None:
        """Persist intake, then resume from the last committed processing stage."""
        super().persist(order, created_at)
        for _ in range(5):
            state = self._read(order["order_id"])["status"]
            if state in {"COMPLETED", "REJECTED"}:
                return
            if state == "RECEIVED":
                with span("orders.payment"):
                    approved = self.approve_payment(order)
                    self._transition(
                        order["order_id"], "RECEIVED", "PAID" if approved else "REJECTED",
                        payment_status="SIMULATED_AUTHORIZED" if approved else "SIMULATED_DECLINED",
                    )
            elif state == "PAID":
                with span("orders.inventory"):
                    self._reserve(order)
            elif state == "RESERVED":
                with span("orders.fulfillment"):
                    shipment_id = self.fulfill(order)
                    self._transition(order["order_id"], "RESERVED", "COMPLETED",
                                     shipment_id=shipment_id, payment_status="SIMULATED_CAPTURED")
            else:
                raise TransientProcessingError("Unsupported order checkpoint")
        raise TransientProcessingError("Processing did not reach a terminal checkpoint")
