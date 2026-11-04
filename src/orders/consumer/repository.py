"""DynamoDB repository for durable order records."""

from __future__ import annotations

from typing import Any

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.config import Config

from orders.consumer.errors import PermanentProcessingError, TransientProcessingError


def create_dynamodb_resource(*, region_name: str | None = None) -> Any:
    """Create a retry-bounded DynamoDB resource using the default credential chain."""
    config = Config(
        connect_timeout=2,
        read_timeout=3,
        retries={"max_attempts": 3, "mode": "standard"},
    )
    return boto3.resource("dynamodb", region_name=region_name, config=config)


class DynamoDBOrderRepository:
    """Persist each order once and verify identical duplicate deliveries."""

    def __init__(
        self, table_name: str, *, dynamodb_resource: Any | None = None,
        key_schema: str = "composite",
    ) -> None:
        if not table_name:
            raise ValueError("table_name must not be empty")
        resource = dynamodb_resource or create_dynamodb_resource()
        self.table = resource.Table(table_name)
        if key_schema not in {"composite", "legacy"}:
            raise ValueError("Unsupported order key schema")
        self.key_schema = key_schema

    def _key(self, order_id: str) -> dict[str, str]:
        if self.key_schema == "legacy":
            return {"order_id": order_id}
        return {"pk": f"ORDER#{order_id}", "sk": "ORDER"}

    def persist(self, order: dict[str, Any], created_at: str) -> None:
        """Create the durable order record or accept an identical existing record."""
        order_id = order["order_id"]
        item = {
            **self._key(order_id),
            "order_id": order_id,
            "items": order["items"],
            "status": "RECEIVED",
            "created_at": created_at,
            "schema_version": 1,
        }
        try:
            key_name = "order_id" if self.key_schema == "legacy" else "pk"
            self.table.put_item(Item=item, ConditionExpression=Attr(key_name).not_exists())
        except self.table.meta.client.exceptions.ConditionalCheckFailedException:
            self.verify_matches(order)

    def verify_matches(self, order: dict[str, Any]) -> None:
        """Confirm a repeated order ID carries the same validated item list."""
        existing = self.table.get_item(
            Key=self._key(order["order_id"]),
            ConsistentRead=True,
        ).get("Item")
        if existing is None:
            raise TransientProcessingError("Completed idempotency record has no order record")
        existing_items = existing.get("items")
        if self.key_schema == "legacy" and isinstance(existing_items, list):
            existing_items = [
                {"sku": item.get("sku", item.get("product_id")), "quantity": item.get("quantity")}
                for item in existing_items
            ]
        if existing_items != order["items"]:
            raise PermanentProcessingError("Order ID already exists with different items")
