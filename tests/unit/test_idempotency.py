import json

import boto3
import pytest
from moto import mock_aws

from orders.consumer.errors import PermanentProcessingError, TransientProcessingError
from orders.consumer.handler import handler
from orders.consumer.idempotency import DynamoDBIdempotencyStore
from orders.consumer.repository import DynamoDBOrderRepository
from orders.shared.validation import ORDER_EVENT_VERSION


def create_table(resource):
    return resource.create_table(
        TableName="orders",
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_aws
def test_dynamodb_idempotency_claim_runs_action_once():
    resource = boto3.resource("dynamodb", region_name="us-east-1")
    table = create_table(resource)
    store = DynamoDBIdempotencyStore("orders", dynamodb_resource=resource, clock=lambda: 1000)
    calls = []

    assert store.execute_once("order-1", lambda: calls.append("processed")) is True
    assert store.execute_once("order-1", lambda: calls.append("duplicate")) is False
    record = table.get_item(Key={"pk": "IDEMPOTENCY#V2#order-1", "sk": "STATE"})["Item"]
    assert record["state"] == "COMPLETE"
    assert record["expires_at"] == 1000 + 30 * 24 * 60 * 60
    assert calls == ["processed"]


@mock_aws
def test_live_in_progress_claim_is_retried_and_expired_claim_can_recover():
    resource = boto3.resource("dynamodb", region_name="us-east-1")
    table = create_table(resource)
    table.put_item(
        Item={
            "pk": "IDEMPOTENCY#V2#order-2",
            "sk": "STATE",
            "state": "IN_PROGRESS",
            "claim_id": "stale",
            "expires_at": 1100,
        }
    )
    store = DynamoDBIdempotencyStore(
        "orders", dynamodb_resource=resource, clock=lambda: 1050, claim_seconds=120
    )
    with pytest.raises(TransientProcessingError):
        store.execute_once("order-2", lambda: None)

    recovered = DynamoDBIdempotencyStore(
        "orders", dynamodb_resource=resource, clock=lambda: 1100, claim_seconds=120
    )
    assert recovered.execute_once("order-2", lambda: None) is True


@mock_aws
def test_order_repository_persists_and_accepts_identical_duplicate():
    resource = boto3.resource("dynamodb", region_name="us-east-1")
    table = create_table(resource)
    repository = DynamoDBOrderRepository("orders", dynamodb_resource=resource)
    order = {"order_id": "order-3", "items": [{"sku": "item-1", "quantity": 2}]}

    repository.persist(order, "2026-11-03T12:00:00Z")
    repository.persist(order, "2026-11-03T12:01:00Z")

    stored = table.get_item(Key={"pk": "ORDER#order-3", "sk": "ORDER"})["Item"]
    assert stored["status"] == "RECEIVED"
    assert stored["items"] == order["items"]
    assert stored["created_at"] == "2026-11-03T12:00:00Z"


@mock_aws
def test_order_repository_rejects_conflicting_reuse_of_order_id():
    resource = boto3.resource("dynamodb", region_name="us-east-1")
    create_table(resource)
    repository = DynamoDBOrderRepository("orders", dynamodb_resource=resource)
    repository.persist(
        {"order_id": "order-4", "items": [{"sku": "item-1", "quantity": 2}]},
        "2026-11-03T12:00:00Z",
    )

    with pytest.raises(PermanentProcessingError, match="different items"):
        repository.persist(
            {"order_id": "order-4", "items": [{"sku": "item-2", "quantity": 1}]},
            "2026-11-03T12:00:00Z",
        )


@mock_aws
def test_consumer_persists_order_once_across_duplicate_delivery(monkeypatch):
    resource = boto3.resource("dynamodb", region_name="us-east-1")
    table = create_table(resource)
    monkeypatch.setenv("ORDERS_TABLE_NAME", "orders")
    order = {"order_id": "order-5", "items": [{"sku": "item-1", "quantity": 3}]}
    record = {
        "messageId": "message-1",
        "body": json.dumps(
            {
                "event_type": "order.created",
                "version": ORDER_EVENT_VERSION,
                "order_id": order["order_id"],
                "order": order,
                "created_at": "2026-11-03T12:00:00Z",
            }
        ),
    }

    assert handler({"Records": [record]}, None, dynamodb_resource=resource) == {
        "batchItemFailures": []
    }
    assert handler({"Records": [record]}, None, dynamodb_resource=resource) == {
        "batchItemFailures": []
    }
    assert table.get_item(Key={"pk": "ORDER#order-5", "sk": "ORDER"})["Item"]["items"] == order[
        "items"
    ]
