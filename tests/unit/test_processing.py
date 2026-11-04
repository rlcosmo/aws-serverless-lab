import json

import boto3
import pytest
from moto import mock_aws

from orders.consumer.errors import PermanentProcessingError, TransientProcessingError
from orders.consumer.handler import handler
from orders.consumer.processing import DynamoDBOrderProcessor


@pytest.fixture
def catalog():
    with mock_aws():
        resource = boto3.resource("dynamodb", region_name="us-east-1")
        table = resource.create_table(
            TableName="processing-test",
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"},
                       {"AttributeName": "sk", "KeyType": "RANGE"}],
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"},
                                  {"AttributeName": "sk", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.put_item(Item={"pk": "INVENTORY#LAB", "sk": "CATALOG", "stock": {"x": 10, "y": 2}})
        yield resource, table


def order(order_id="flow-1", items=None):
    return {"order_id": order_id, "items": items or [{"sku": "x", "quantity": 3}]}


def state(table, order_id="flow-1"):
    return table.get_item(Key={"pk": f"ORDER#{order_id}", "sk": "ORDER"})["Item"]


def stock(table):
    return table.get_item(Key={"pk": "INVENTORY#LAB", "sk": "CATALOG"})["Item"]["stock"]


def test_payment_inventory_fulfillment_and_duplicate(catalog):
    resource, table = catalog
    processor = DynamoDBOrderProcessor(table.name, dynamodb_resource=resource)
    processor.persist(order(), "2026-11-04T00:00:00Z")
    processor.persist(order(), "2026-11-04T00:00:01Z")
    result = state(table)
    assert result["status"] == "COMPLETED"
    assert result["payment_status"] == "SIMULATED_CAPTURED"
    assert result["shipment_id"].startswith("sim-shipment-")
    assert stock(table)["x"] == 7


def test_conflicting_duplicate_does_not_change_stock(catalog):
    resource, table = catalog
    processor = DynamoDBOrderProcessor(table.name, dynamodb_resource=resource)
    processor.persist(order(), "2026-11-04T00:00:00Z")
    with pytest.raises(PermanentProcessingError):
        processor.persist(order(items=[{"sku": "x", "quantity": 4}]), "2026-11-04T00:00:00Z")
    assert stock(table)["x"] == 7


def test_duplicate_skus_are_aggregated(catalog):
    resource, table = catalog
    processor = DynamoDBOrderProcessor(table.name, dynamodb_resource=resource)
    processor.persist(order(items=[{"sku": "x", "quantity": 2}, {"sku": "x", "quantity": 4}]),
                      "2026-11-04T00:00:00Z")
    assert state(table)["status"] == "COMPLETED"
    assert stock(table)["x"] == 4


def test_declined_payment_does_not_reserve_inventory(catalog):
    resource, table = catalog
    processor = DynamoDBOrderProcessor(table.name, dynamodb_resource=resource,
                                      approve_payment=lambda value: False)
    processor.persist(order(), "2026-11-04T00:00:00Z")
    assert state(table)["status"] == "REJECTED"
    assert state(table)["payment_status"] == "SIMULATED_DECLINED"
    assert stock(table)["x"] == 10


@pytest.mark.parametrize("sku,quantity", [("y", 3), ("unknown", 1)])
def test_reservation_is_atomic_and_simulated_payment_is_refunded(catalog, sku, quantity):
    resource, table = catalog
    processor = DynamoDBOrderProcessor(table.name, dynamodb_resource=resource)
    processor.persist(order(items=[{"sku": "x", "quantity": 3}, {"sku": sku, "quantity": quantity}]),
                      "2026-11-04T00:00:00Z")
    assert state(table)["status"] == "REJECTED"
    assert state(table)["payment_status"] == "SIMULATED_REFUNDED"
    assert stock(table) == {"x": 10, "y": 2}


def test_two_orders_cannot_oversell(catalog):
    resource, table = catalog
    processor = DynamoDBOrderProcessor(table.name, dynamodb_resource=resource)
    items = [{"sku": "x", "quantity": 7}]
    processor.persist(order("first", items), "2026-11-04T00:00:00Z")
    processor.persist(order("second", items), "2026-11-04T00:00:00Z")
    assert state(table, "first")["status"] == "COMPLETED"
    assert state(table, "second")["status"] == "REJECTED"
    assert stock(table)["x"] == 3


def test_missing_inventory_configuration_is_retryable(catalog):
    resource, table = catalog
    table.delete_item(Key={"pk": "INVENTORY#LAB", "sk": "CATALOG"})
    processor = DynamoDBOrderProcessor(table.name, dynamodb_resource=resource)
    with pytest.raises(TransientProcessingError, match="not configured"):
        processor.persist(order(), "2026-11-04T00:00:00Z")
    assert state(table)["status"] == "PAID"


def test_retry_after_fulfillment_failure_does_not_reserve_again(catalog):
    resource, table = catalog

    def fail(_):
        raise TransientProcessingError("simulated outage")

    processor = DynamoDBOrderProcessor(table.name, dynamodb_resource=resource, fulfill=fail)
    with pytest.raises(TransientProcessingError):
        processor.persist(order(), "2026-11-04T00:00:00Z")
    assert state(table)["status"] == "RESERVED"
    assert stock(table)["x"] == 7
    DynamoDBOrderProcessor(table.name, dynamodb_resource=resource).persist(
        order(), "2026-11-04T00:00:00Z",
    )
    assert state(table)["status"] == "COMPLETED"
    assert stock(table)["x"] == 7


def test_handler_complete_mode_reprocesses_old_intake_checkpoint(catalog, monkeypatch):
    resource, table = catalog
    table.put_item(Item={"pk": "ORDER#flow-1", "sk": "ORDER", "items": order()["items"],
                        "status": "RECEIVED"})
    table.put_item(Item={"pk": "IDEMPOTENCY#V2#flow-1", "sk": "STATE", "state": "COMPLETE",
                        "expires_at": 9999999999})
    monkeypatch.setenv("ORDERS_TABLE_NAME", table.name)
    monkeypatch.setenv("ORDERS_PROCESSING_MODE", "complete")
    record = {"messageId": "m1", "body": json.dumps({"event_type": "order.created", "version": 2,
              "order_id": "flow-1", "order": order(), "created_at": "2026-11-04T00:00:00Z"})}
    assert handler({"Records": [record]}, None, dynamodb_resource=resource) == {"batchItemFailures": []}
    assert handler({"Records": [record]}, None, dynamodb_resource=resource) == {"batchItemFailures": []}
    assert state(table)["status"] == "COMPLETED"
    assert stock(table)["x"] == 7


def test_partial_sqs_batch_keeps_invalid_messages_for_retry(catalog, monkeypatch):
    resource, table = catalog
    monkeypatch.setenv("ORDERS_TABLE_NAME", table.name)
    monkeypatch.setenv("ORDERS_PROCESSING_MODE", "complete")
    good = {"messageId": "good", "body": json.dumps({"event_type": "order.created", "version": 2,
            "order_id": "flow-1", "order": order(), "created_at": "2026-11-04T00:00:00Z"})}
    bad = {"messageId": "invalid", "body": '{"invalid":true}'}
    assert handler({"Records": [bad, good]}, None, dynamodb_resource=resource) == {
        "batchItemFailures": [{"itemIdentifier": "invalid"}],
    }
    assert state(table)["status"] == "COMPLETED"
