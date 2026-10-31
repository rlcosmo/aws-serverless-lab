"""API Gateway compatible Lambda handler that enqueues validated orders."""

import json
import os
import base64
import binascii
from typing import Any

import boto3
from botocore.config import Config

from orders.shared.logging import get_logger
from orders.shared.validation import MAX_REQUEST_BYTES, OrderValidationError, validate_order

logger = get_logger(__name__)


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }


def handler(
    event: dict[str, Any], context: Any, *, sqs_client: Any | None = None
) -> dict[str, Any]:
    """Validate an API request and publish a minimal event to SQS."""
    try:
        raw_body = event.get("body")
        if event.get("isBase64Encoded") is True:
            if not isinstance(raw_body, str):
                raise OrderValidationError("Request body must be text")
            if len(raw_body) > ((MAX_REQUEST_BYTES + 2) // 3) * 4:
                raise OrderValidationError("Request body exceeds the maximum size")
            try:
                raw_body = base64.b64decode(raw_body, validate=True).decode("utf-8")
            except (binascii.Error, UnicodeDecodeError, ValueError) as exc:
                raise OrderValidationError("Request body is not valid Base64-encoded UTF-8") from exc
        if isinstance(raw_body, str):
            if len(raw_body.encode("utf-8")) > MAX_REQUEST_BYTES:
                raise OrderValidationError("Request body exceeds the maximum size")
            payload = json.loads(raw_body)
        elif raw_body is None:
            payload = None
        else:
            raise OrderValidationError("Request body must be text")
        order = validate_order(payload)
    except (json.JSONDecodeError, OrderValidationError, AttributeError, TypeError):
        logger.info("order_rejected", extra={"event": "order_rejected", "reason": "invalid_request"})
        return _response(400, {"error": "Invalid request"})

    queue_url = os.environ.get("ORDERS_QUEUE_URL")
    if not queue_url:
        logger.error("queue_configuration_missing", extra={"event": "configuration_error"})
        return _response(500, {"error": "Service configuration error"})

    client = sqs_client or boto3.client(
        "sqs",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        config=Config(
            connect_timeout=2,
            read_timeout=3,
            retries={"max_attempts": 2, "mode": "standard"},
        ),
    )
    message = {"event_type": "order.created", "version": 1, "order_id": order["order_id"]}
    try:
        client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
    except Exception as exc:
        logger.error(
            "order_enqueue_failed",
            extra={"event": "order_enqueue_failed", "error_type": type(exc).__name__},
        )
        return _response(503, {"error": "Order could not be queued"})

    logger.info("order_accepted", extra={"event": "order_accepted"})
    return _response(202, {"order_id": order["order_id"], "status": "PENDING"})
