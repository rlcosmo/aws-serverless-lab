import json

import boto3
from moto import mock_aws

from orders.consumer.handler import handler


@mock_aws
def test_invalid_contract_retries_then_moves_to_dlq_without_acknowledgment():
    client = boto3.client("sqs", region_name="us-east-1")
    dlq = client.create_queue(QueueName="test-dead-letter")["QueueUrl"]
    arn = client.get_queue_attributes(QueueUrl=dlq, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]
    queue = client.create_queue(QueueName="test-source", Attributes={
        "VisibilityTimeout": "0",
        "RedrivePolicy": json.dumps({"deadLetterTargetArn": arn, "maxReceiveCount": 2}),
    })["QueueUrl"]
    client.send_message(QueueUrl=queue, MessageBody='{"invalid":true}')
    failures = 0
    for _ in range(4):
        messages = client.receive_message(QueueUrl=queue, VisibilityTimeout=0).get("Messages", [])
        if not messages:
            break
        message = messages[0]
        result = handler({"Records": [{"messageId": message["MessageId"],
                                       "body": message["Body"]}]}, None)
        assert result["batchItemFailures"] == [{"itemIdentifier": message["MessageId"]}]
        failures += 1
    assert failures == 2
    dead = client.receive_message(QueueUrl=dlq)["Messages"][0]
    assert json.loads(dead["Body"]) == {"invalid": True}
