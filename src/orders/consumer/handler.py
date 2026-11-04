"""SQS batch handler that durably records orders with partial failures."""

import json
import os
from collections.abc import Callable
from typing import Any, Protocol

from orders.consumer.errors import PermanentProcessingError, TransientProcessingError
from orders.consumer.idempotency import DynamoDBIdempotencyStore
from orders.consumer.processing import DynamoDBOrderProcessor
from orders.consumer.repository import DynamoDBOrderRepository, create_dynamodb_resource
from orders.shared.logging import get_logger
from orders.shared.tracing import span
from orders.shared.validation import OrderValidationError, validate_order_event

logger = get_logger(__name__)


class IdempotencyStore(Protocol):
    """Durable boundary for suppressing duplicate SQS delivery."""

    def execute_once(self, key: str, action: Callable[[], None]) -> bool:
        """Run action once per key, returning false for a completed duplicate."""


class OrderRepository(Protocol):
    """Persistence boundary for a validated order."""

    def persist(self, order: dict[str, Any], created_at: str) -> None:
        """Persist an order or accept a matching prior write."""

    def verify_matches(self, order: dict[str, Any]) -> None:
        """Verify an existing durable order matches a repeated request."""


def handler(
    event: dict[str, Any],
    context: Any,
    *,
    idempotency_store: IdempotencyStore | None = None,
    order_repository: OrderRepository | None = None,
    dynamodb_resource: Any | None = None,
) -> dict[str, list[dict[str, str]]]:
    """Persist valid messages and report only failed SQS record identifiers."""
    table_name = os.environ.get("ORDERS_TABLE_NAME")
    complete_processing = os.environ.get("ORDERS_PROCESSING_MODE", "intake") == "complete"
    if table_name and (idempotency_store is None or order_repository is None):
        resource = dynamodb_resource or create_dynamodb_resource(
            region_name=os.getenv("AWS_REGION")
        )
        idempotency_store = idempotency_store or DynamoDBIdempotencyStore(
            table_name, dynamodb_resource=resource, namespace="V3" if complete_processing else "V2"
        )
        repository_class = DynamoDBOrderProcessor if complete_processing else DynamoDBOrderRepository
        order_repository = order_repository or repository_class(
            table_name, dynamodb_resource=resource
        )

    failures: list[dict[str, str]] = []
    records = event.get("Records", [])
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("messageId"), str):
            raise TypeError("SQS record is missing messageId")
        message_id = record["messageId"]
        try:
            order_event = validate_order_event(json.loads(record["body"]))
        except (KeyError, json.JSONDecodeError, OrderValidationError, TypeError):
            logger.warning(
                "invalid_order_message",
                extra={"event": "invalid_order_message", "reason": "invalid_contract"},
            )
            failures.append({"itemIdentifier": message_id})
            continue

        try:
            if idempotency_store is None or order_repository is None:
                raise TransientProcessingError("DynamoDB order storage is not configured")

            attributes = record.get("messageAttributes", {})
            carrier = {
                key: value["stringValue"] for key, value in attributes.items()
                if key in {"traceparent", "tracestate"} and isinstance(value, dict)
                and isinstance(value.get("stringValue"), str)
            }
            with span("orders.consume", carrier):
                executed = idempotency_store.execute_once(
                    order_event["order_id"],
                    lambda order=order_event["order"], created_at=order_event["created_at"]: (
                        order_repository.persist(order, created_at)
                    ),
                )
            if not executed:
                order_repository.verify_matches(order_event["order"])
            logger.info("order_persisted", extra={"event": "order_persisted"})
        except PermanentProcessingError as exc:
            logger.warning(
                "permanent_order_failure",
                extra={"event": "permanent_failure", "error_type": type(exc).__name__},
            )
            failures.append({"itemIdentifier": message_id})
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "order_processing_failed",
                extra={"event": "transient_failure", "error_type": type(exc).__name__},
            )
            failures.append({"itemIdentifier": message_id})
    return {"batchItemFailures": failures}
