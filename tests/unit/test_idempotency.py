import json

import boto3
import pytest
from moto import mock_aws

from orders.consumer.handler import TransientProcessingError
from orders.consumer.idempotency import DynamoDBIdempotencyStore


def create_table(client):
    client.create_table(
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
    client = boto3.client("dynamodb", region_name="us-east-1")
    create_table(client)
    store = DynamoDBIdempotencyStore("orders", dynamodb_client=client, clock=lambda: 1000)
    calls = []

    assert store.execute_once("order-1", lambda: calls.append("processed")) is True
    assert store.execute_once("order-1", lambda: calls.append("duplicate")) is False
    record = client.get_item(
        TableName="orders",
        Key={"pk": {"S": "IDEMPOTENCY#order-1"}, "sk": {"S": "STATE"}},
    )["Item"]
    assert record["state"]["S"] == "COMPLETE"
    assert record["expires_at"]["N"] == str(1000 + 30 * 24 * 60 * 60)
    assert calls == ["processed"]


@mock_aws
def test_live_in_progress_claim_is_retried_and_expired_claim_can_recover():
    client = boto3.client("dynamodb", region_name="us-east-1")
    create_table(client)
    client.put_item(
        TableName="orders",
        Item={
            "pk": {"S": "IDEMPOTENCY#order-2"},
            "sk": {"S": "STATE"},
            "state": {"S": "IN_PROGRESS"},
            "claim_id": {"S": "stale"},
            "expires_at": {"N": "1100"},
        },
    )
    store = DynamoDBIdempotencyStore(
        "orders", dynamodb_client=client, clock=lambda: 1050, claim_seconds=120
    )
    with pytest.raises(TransientProcessingError):
        store.execute_once("order-2", lambda: None)

    recovered = DynamoDBIdempotencyStore(
        "orders", dynamodb_client=client, clock=lambda: 1100, claim_seconds=120
    )
    assert recovered.execute_once("order-2", lambda: None) is True


@mock_aws
def test_consumer_handler_uses_configured_dynamodb_store(monkeypatch):
    client = boto3.client("dynamodb", region_name="us-east-1")
    create_table(client)
    from orders.consumer import handler as consumer_module
    from orders.consumer import idempotency as idempotency_module

    calls = []
    monkeypatch.setenv("ORDERS_TABLE_NAME", "orders")
    monkeypatch.setattr(idempotency_module.boto3, "client", lambda *args, **kwargs: client)
    monkeypatch.setattr(consumer_module, "process_order", lambda order_id: calls.append(order_id))
    record = {
        "messageId": "message-1",
        "body": json.dumps(
            {"event_type": "order.created", "version": 1, "order_id": "order-3"}
        ),
    }

    assert consumer_module.handler({"Records": [record]}, None) == {"batchItemFailures": []}
    assert consumer_module.handler({"Records": [record]}, None) == {"batchItemFailures": []}
    assert calls == ["order-3"]
