"""Validation rules for order requests and queue events."""

from typing import Any

MAX_REQUEST_BYTES = 256 * 1024
MAX_ORDER_ID_LENGTH = 128
MAX_ITEMS = 100
MAX_SKU_LENGTH = 128
MAX_QUANTITY = 10_000


class OrderValidationError(ValueError):
    """Raised when an order does not meet the application contract."""


def validate_order(payload: Any) -> dict[str, Any]:
    """Validate and normalize the public order fields."""
    if not isinstance(payload, dict):
        raise OrderValidationError("Request body must be a JSON object")

    order_id = payload.get("order_id")
    items = payload.get("items")
    if not isinstance(order_id, str) or not order_id.strip() or len(order_id.strip()) > MAX_ORDER_ID_LENGTH:
        raise OrderValidationError("order_id must contain 1 to 128 characters")
    if not isinstance(items, list) or not items or len(items) > MAX_ITEMS:
        raise OrderValidationError("items must contain between 1 and 100 entries")

    normalized_items: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise OrderValidationError(f"items[{index}] must be an object")
        sku = item.get("sku")
        quantity = item.get("quantity")
        if not isinstance(sku, str) or not sku.strip() or len(sku.strip()) > MAX_SKU_LENGTH:
            raise OrderValidationError(f"items[{index}].sku must contain 1 to 128 characters")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or not 1 <= quantity <= MAX_QUANTITY:
            raise OrderValidationError(f"items[{index}].quantity must be between 1 and 10000")
        normalized_items.append({"sku": sku.strip(), "quantity": quantity})

    return {"order_id": order_id.strip(), "items": normalized_items}


def validate_order_event(event: Any) -> dict[str, Any]:
    """Validate the versioned, minimal event sent through SQS."""
    if not isinstance(event, dict):
        raise OrderValidationError("Event must be a JSON object")
    version = event.get("version")
    if event.get("event_type") != "order.created" or type(version) is not int or version != 1:
        raise OrderValidationError("Unsupported event type or version")
    order_id = event.get("order_id")
    if not isinstance(order_id, str) or not order_id.strip() or len(order_id.strip()) > MAX_ORDER_ID_LENGTH:
        raise OrderValidationError("order_id must contain 1 to 128 characters")
    return {"event_type": "order.created", "version": 1, "order_id": order_id.strip()}
