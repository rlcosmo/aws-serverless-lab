import base64
import io
import json

import pytest
from moto import mock_aws
import boto3

from orders.consumer.handler import (
    PermanentProcessingError,
    TransientProcessingError,
    handler as consumer_handler,
)
from orders.producer.handler import handler as producer_handler
from orders.shared.validation import MAX_REQUEST_BYTES


@mock_aws
def test_producer_validates_and_enqueues_order(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("ORDERS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/orders")
    sqs = boto3.client("sqs", region_name="us-east-1")
    queue_url = sqs.create_queue(QueueName="orders")["QueueUrl"]
    monkeypatch.setenv("ORDERS_QUEUE_URL", queue_url)

    response = producer_handler({"body": json.dumps({"order_id": "o-1", "items": [{"sku": "x", "quantity": 1}]})}, None, sqs_client=sqs)

    assert response["statusCode"] == 202
    assert json.loads(response["body"])["order_id"] == "o-1"
    assert json.loads(sqs.receive_message(QueueUrl=queue_url)["Messages"][0]["Body"])["order_id"] == "o-1"


def test_producer_rejects_bad_json():
    assert producer_handler({"body": "{"}, None)["statusCode"] == 400


def test_producer_decodes_base64_body(monkeypatch):
    from orders.producer import handler as producer_module

    class Queue:
        body = None

        def send_message(self, **kwargs):
            self.body = kwargs["MessageBody"]

    queue = Queue()
    monkeypatch.setenv("ORDERS_QUEUE_URL", "queue-url")
    response = producer_module.handler(
        {
            "body": base64.b64encode(
                json.dumps({"order_id": "o-1", "items": [{"sku": "x", "quantity": 1}]}).encode()
            ).decode(),
            "isBase64Encoded": True,
        },
        None,
        sqs_client=queue,
    )
    assert response["statusCode"] == 202
    assert json.loads(queue.body)["order_id"] == "o-1"


@pytest.mark.parametrize(
    "body",
    [
        "not base64!",
        base64.b64encode(b"not utf-8: \xff").decode(),
        base64.b64encode(b" " * (MAX_REQUEST_BYTES + 1)).decode(),
    ],
)
def test_producer_rejects_invalid_or_oversized_base64(body, monkeypatch):
    monkeypatch.setenv("ORDERS_QUEUE_URL", "queue-url")
    response = producer_handler({"body": body, "isBase64Encoded": True}, None, sqs_client=object())
    assert response["statusCode"] == 400


def test_producer_rejects_oversized_json_body(monkeypatch):
    monkeypatch.setenv("ORDERS_QUEUE_URL", "queue-url")
    response = producer_handler({"body": " " * (MAX_REQUEST_BYTES + 1)}, None, sqs_client=object())
    assert response["statusCode"] == 400


def test_producer_rejects_non_text_body(monkeypatch):
    monkeypatch.setenv("ORDERS_QUEUE_URL", "queue-url")
    response = producer_handler(
        {"body": {"order_id": "o-1", "items": [{"sku": "x", "quantity": 1}]}},
        None,
        sqs_client=object(),
    )
    assert response["statusCode"] == 400


def test_producer_returns_generic_temporary_error_without_logging_payload(monkeypatch, capsys):
    monkeypatch.setenv("ORDERS_QUEUE_URL", "queue-url")

    class FailingQueue:
        def send_message(self, **kwargs):
            raise RuntimeError("secret queue response")

    response = producer_handler(
        {"body": json.dumps({"order_id": "sensitive-id", "items": [{"sku": "x", "quantity": 1}]})},
        None,
        sqs_client=FailingQueue(),
    )
    log_output = capsys.readouterr().out
    assert response["statusCode"] == 503
    assert "secret queue response" not in log_output
    assert "sensitive-id" not in log_output


def test_producer_configures_bounded_aws_timeouts_and_retries(monkeypatch):
    from orders.producer import handler as producer_module

    captured = {}

    class Queue:
        def send_message(self, **kwargs):
            return {}

    def create_client(service, **kwargs):
        captured.update(service=service, **kwargs)
        return Queue()

    monkeypatch.setattr(producer_module.boto3, "client", create_client)
    monkeypatch.setenv("ORDERS_QUEUE_URL", "queue-url")
    result = producer_module.handler(
        {"body": json.dumps({"order_id": "o-1", "items": [{"sku": "x", "quantity": 1}]})},
        None,
    )
    config = captured["config"]
    assert result["statusCode"] == 202
    assert captured["service"] == "sqs"
    assert config.connect_timeout == 2
    assert config.read_timeout == 3
    assert config.retries["max_attempts"] == 2


def test_consumer_reports_only_failed_records(monkeypatch):
    from orders.consumer import handler as consumer_module

    def fail(order_id):
        raise RuntimeError("temporary failure")

    monkeypatch.setattr(consumer_module, "process_order", fail)
    result = consumer_module.handler({"Records": [
        {"messageId": "good", "body": json.dumps({"event_type": "order.created", "version": 1, "order_id": "o-1"})},
        {"messageId": "bad", "body": "not-json"},
    ]}, None)
    assert result == {"batchItemFailures": [{"itemIdentifier": "good"}, {"itemIdentifier": "bad"}]}


def test_consumer_accepts_valid_record():
    result = consumer_handler({"Records": [{"messageId": "m-1", "body": json.dumps({"event_type": "order.created", "version": 1, "order_id": "o-1"})}]}, None)
    assert result == {"batchItemFailures": []}


@pytest.mark.parametrize("body", ["not-json", json.dumps({"event_type": "order.created", "version": True, "order_id": "o-1"})])
def test_consumer_sends_invalid_messages_to_retry_and_redrive(body):
    result = consumer_handler({"Records": [{"messageId": "invalid", "body": body}]}, None)
    assert result == {"batchItemFailures": [{"itemIdentifier": "invalid"}]}


def test_consumer_distinguishes_permanent_and_transient_failures(monkeypatch):
    from orders.consumer import handler as consumer_module

    log_stream = io.StringIO()
    monkeypatch.setattr(consumer_module.logger.handlers[0], "stream", log_stream)

    def process(order_id):
        if order_id == "permanent":
            raise PermanentProcessingError("bad business state")
        raise TransientProcessingError("temporary dependency outage")

    monkeypatch.setattr(consumer_module, "process_order", process)
    messages = [
        {"messageId": order_id, "body": json.dumps({"event_type": "order.created", "version": 1, "order_id": order_id})}
        for order_id in ("permanent", "transient")
    ]
    result = consumer_module.handler({"Records": messages}, None)
    output = log_stream.getvalue()
    assert result["batchItemFailures"] == [
        {"itemIdentifier": "permanent"},
        {"itemIdentifier": "transient"},
    ]
    assert '"event": "permanent_failure"' in output
    assert '"event": "transient_failure"' in output
    assert "bad business state" not in output
    assert "temporary dependency outage" not in output


def test_consumer_delegates_duplicate_suppression_to_durable_store_contract(monkeypatch):
    from orders.consumer import handler as consumer_module

    class TestStore:
        """Test double only; production idempotency requires a durable implementation."""

        completed = set()

        def execute_once(self, key, action):
            if key in self.completed:
                return False
            action()
            self.completed.add(key)
            return True

    calls = []
    monkeypatch.setattr(consumer_module, "process_order", lambda order_id: calls.append(order_id))
    message = {"messageId": "m-1", "body": json.dumps({"event_type": "order.created", "version": 1, "order_id": "o-1"})}
    store = TestStore()
    first = consumer_module.handler({"Records": [message]}, None, idempotency_store=store)
    second = consumer_module.handler({"Records": [message]}, None, idempotency_store=store)
    assert first["batchItemFailures"] == second["batchItemFailures"] == []
    assert calls == ["o-1"]


def test_consumer_requires_message_id_to_report_partial_failure():
    with pytest.raises(ValueError, match="messageId"):
        consumer_handler({"Records": [{"body": "not-json"}]}, None)
