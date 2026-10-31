import pytest
from orders.shared.validation import (
    MAX_ITEMS,
    MAX_ORDER_ID_LENGTH,
    MAX_QUANTITY,
    MAX_REQUEST_BYTES,
    MAX_SKU_LENGTH,
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
    assert validate_order_event({"event_type": "order.created", "version": 1, "order_id": "o-1"})["order_id"] == "o-1"


@pytest.mark.parametrize("version", [True, False, 1.0, "1", 2, None])
def test_validate_order_event_rejects_non_integer_or_unsupported_version(version):
    with pytest.raises(OrderValidationError):
        validate_order_event({"event_type": "order.created", "version": version, "order_id": "o-1"})


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
