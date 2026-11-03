import pytest

from orders.shared.validation import (
    MAX_ITEMS,
    MAX_ORDER_ID_LENGTH,
    MAX_QUANTITY,
    MAX_REQUEST_BYTES,
    MAX_SKU_LENGTH,
    ORDER_EVENT_VERSION,
    OrderValidationError,
    validate_order,
    validate_order_event,
)


def test_validate_order_normalizes_fields():
    assert validate_order({"order_id": " o-1 ", "items": [{"sku": " x ", "quantity": 2}]}) == {
        "order_id": "o-1",
        "items": [{"sku": "x", "quantity": 2}],
    }


@pytest.mark.parametrize(
    "payload",
    [None, {}, {"order_id": "x", "items": []}, {"order_id": "x", "items": [{"sku": "x", "quantity": True}] }],
)
def test_validate_order_rejects_invalid_payload(payload):
    with pytest.raises(OrderValidationError):
        validate_order(payload)


def test_validate_order_event_accepts_supported_contract():
    event = validate_order_event(
        {
            "event_type": "order.created",
            "version": ORDER_EVENT_VERSION,
            "order_id": "o-1",
            "order": {"order_id": "o-1", "items": [{"sku": "x", "quantity": 1}]},
            "created_at": "2026-11-03T12:00:00Z",
        }
    )
    assert event["order_id"] == "o-1"
    assert event["order"]["items"] == [{"sku": "x", "quantity": 1}]
    assert event["created_at"] == "2026-11-03T12:00:00Z"


@pytest.mark.parametrize("version", [True, False, 1.0, "2", 1, None])
def test_validate_order_event_rejects_non_integer_or_unsupported_version(version):
    with pytest.raises(OrderValidationError):
        validate_order_event({"event_type": "order.created", "version": version, "order_id": "o-1"})


@pytest.mark.parametrize(
    "order,created_at",
    [
        ({"order_id": "o-2", "items": [{"sku": "x", "quantity": 1}]}, "2026-11-03T12:00:00Z"),
        ({"order_id": "o-1", "items": [{"sku": "x", "quantity": 1}]}, "2026-11-03T12:00:00"),
        ({"order_id": "o-1", "items": []}, "2026-11-03T12:00:00Z"),
    ],
)
def test_validate_order_event_rejects_mismatched_or_invalid_payload(order, created_at):
    with pytest.raises(OrderValidationError):
        validate_order_event(
            {
                "event_type": "order.created",
                "version": ORDER_EVENT_VERSION,
                "order_id": "o-1",
                "order": order,
                "created_at": created_at,
            }
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"order_id": "x" * (MAX_ORDER_ID_LENGTH + 1), "items": [{"sku": "x", "quantity": 1}]},
        {"order_id": "x", "items": [{"sku": "x" * (MAX_SKU_LENGTH + 1), "quantity": 1}]},
        {"order_id": "x", "items": [{"sku": "x", "quantity": MAX_QUANTITY + 1}]},
        {"order_id": "x", "items": [{"sku": "x", "quantity": 1}] * (MAX_ITEMS + 1)},
    ],
)
def test_validate_order_rejects_values_above_limits(payload):
    with pytest.raises(OrderValidationError):
        validate_order(payload)


def test_validation_limits_allow_maximum_values():
    order = validate_order(
        {
            "order_id": "o" * MAX_ORDER_ID_LENGTH,
            "items": [
                {"sku": "s" * MAX_SKU_LENGTH, "quantity": MAX_QUANTITY}
            ]
            * MAX_ITEMS,
        }
    )
    assert len(order["items"]) == MAX_ITEMS


def test_request_body_limit_is_defined():
    assert MAX_REQUEST_BYTES == 256 * 1024
