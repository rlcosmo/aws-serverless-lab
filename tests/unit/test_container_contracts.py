import json

import boto3
import pytest
from moto import mock_aws

from orders.consumer.processing import DynamoDBOrderProcessor
from orders.runtime.api import normalize_request
from orders.runtime.worker import process_message


@mock_aws
def test_legacy_eks_contract_and_table_reach_full_processing_without_schema_replacement():
    resource = boto3.resource("dynamodb", region_name="us-east-1")
    table = resource.create_table(TableName="legacy-orders",
        KeySchema=[{"AttributeName": "order_id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "order_id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST")
    table.put_item(Item={"order_id": "INVENTORY#LAB", "stock": {"product-1": 5}})
    processor = DynamoDBOrderProcessor(table.name, dynamodb_resource=resource, key_schema="legacy")
    event = {"order_id": "existing-contract", "customer_id": "lab-only",
             "items": [{"product_id": "product-1", "quantity": 2}],
             "created_at": "2026-11-04T00:00:00Z"}
    process_message({"Body": json.dumps(event)}, processor)
    process_message({"Body": json.dumps(event)}, processor)
    assert table.get_item(Key={"order_id": event["order_id"]})["Item"]["status"] == "COMPLETED"
    assert table.get_item(Key={"order_id": "INVENTORY#LAB"})["Item"]["stock"]["product-1"] == 3
    # A record completed by the previous worker is not processed again.
    table.put_item(Item={**event, "order_id": "old-completed", "status": "COMPLETED"})
    event["order_id"] = "old-completed"
    process_message({"Body": json.dumps(event)}, processor)
    assert table.get_item(Key={"order_id": "INVENTORY#LAB"})["Item"]["stock"]["product-1"] == 3


def test_legacy_http_request_normalizes_product_id_and_preserves_explicit_id():
    payload = {"customer_id": "lab", "items": [{"product_id": "x", "quantity": 1}]}
    first = normalize_request(payload)
    assert first["order_id"]
    assert first["items"] == [{"sku": "x", "quantity": 1}]
    assert normalize_request({**payload, "order_id": "client-id"})["order_id"] == "client-id"


def test_worker_rejects_invalid_legacy_input_before_aws_access():
    class NoWrite:
        def persist(self, *args):
            pytest.fail("Invalid input must not reach storage")

    with pytest.raises(ValueError):
        process_message({"Body": '{"invalid":true}'}, NoWrite())
