"""SQS batch handler with partial failures and an injectable idempotency boundary."""

import json
import os
from collections.abc import Callable
from typing import Any, Protocol

from orders.shared.logging import get_logger
from orders.shared.validation import OrderValidationError, validate_order_event

logger = get_logger(__name__)


class PermanentProcessingError(Exception):
    """A validly decoded event that cannot succeed if retried unchanged."""


class TransientProcessingError(Exception):
    """A temporary processing or dependency failure that can succeed on retry."""


class IdempotencyStore(Protocol):
    """Durable boundary required for duplicate suppression (for example DynamoDB)."""

    def execute_once(self, key: str, action: Callable[[], None]) -> bool:
        """Atomically run action once; return False when key was already completed.

        Implementations must use durable conditional state and define recovery for
        interrupted/in-progress work. An in-memory cache is not sufficient.
        """


def process_order(order_id: str) -> None:
    """Application seam; persistence and business effects are not implemented yet."""
    logger.info("order_processing_seam_called", extra={"event": "processing_seam_called"})


def handler(
    event: dict[str, Any],
    context: Any,
    *,
    idempotency_store: IdempotencyStore | None = None,
) -> dict[str, list[dict[str, str]]]:
    """Process records, retrying failures individually when SQS partial responses are enabled.

    Invalid/permanent messages are returned as failures so the queue redrive policy
    can move them to a DLQ after its receive limit. Unknown processing errors are
    treated as transient. Without a durable store, duplicate suppression is absent.
    """
    failures: list[dict[str, str]] = []
    if idempotency_store is None and os.environ.get("ORDERS_TABLE_NAME"):
        from orders.consumer.idempotency import DynamoDBIdempotencyStore

        idempotency_store = DynamoDBIdempotencyStore(os.environ["ORDERS_TABLE_NAME"])
    records = event.get("Records", [])
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("messageId"), str):
            # There is no identifier to put in batchItemFailures; fail invocation.
            raise ValueError("SQS record is missing messageId")
        message_id = record["messageId"]
        try:
            body = json.loads(record["body"])
            order_event = validate_order_event(body)
        except (KeyError, json.JSONDecodeError, OrderValidationError, TypeError):
            logger.warning(
                "invalid_order_message",
                extra={"event": "invalid_order_message", "reason": "invalid_contract"},
            )
            failures.append({"itemIdentifier": message_id})
            continue

        try:
            if idempotency_store is None:
                logger.warning(
                    "idempotency_store_unconfigured",
                    extra={"event": "idempotency_unconfigured"},
                )
                process_order(order_event["order_id"])
            else:
                executed = idempotency_store.execute_once(
                    order_event["order_id"],
                    lambda: process_order(order_event["order_id"]),
                )
                if not executed:
                    logger.info("duplicate_order_skipped", extra={"event": "duplicate_skipped"})
        except PermanentProcessingError as exc:
            logger.warning(
                "permanent_order_failure",
                extra={"event": "permanent_failure", "error_type": type(exc).__name__},
            )
            failures.append({"itemIdentifier": message_id})
        except Exception as exc:
            # Includes explicit transient failures and unknown dependency errors.
            logger.error(
                "order_processing_failed",
                extra={"event": "transient_failure", "error_type": type(exc).__name__},
            )
            failures.append({"itemIdentifier": message_id})
    return {"batchItemFailures": failures}
