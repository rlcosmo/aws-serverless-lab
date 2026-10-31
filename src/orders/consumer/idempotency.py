"""DynamoDB-backed idempotency claim with lease-based recovery."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import Any

import boto3
from botocore.exceptions import ClientError

from orders.consumer.handler import TransientProcessingError

DEFAULT_CLAIM_SECONDS = 120
DEFAULT_COMPLETED_TTL_SECONDS = 30 * 24 * 60 * 60


class DynamoDBIdempotencyStore:
    """Run an action once per key using conditional DynamoDB updates.

    In-progress records expire logically at `claim_seconds`, allowing a later
    delivery to recover after a crashed invocation. Completed records use a
    longer TTL; DynamoDB TTL deletion itself is asynchronous.
    """

    def __init__(
        self,
        table_name: str,
        *,
        dynamodb_client: Any | None = None,
        clock: Callable[[], float] = time.time,
        claim_seconds: int = DEFAULT_CLAIM_SECONDS,
        completed_ttl_seconds: int = DEFAULT_COMPLETED_TTL_SECONDS,
    ) -> None:
        if not table_name:
            raise ValueError("table_name must not be empty")
        self.table_name = table_name
        self.client = dynamodb_client
        self.clock = clock
        self.claim_seconds = claim_seconds
        self.completed_ttl_seconds = completed_ttl_seconds

    def _client(self) -> Any:
        if self.client is None:
            self.client = boto3.client("dynamodb")
        return self.client

    def execute_once(self, key: str, action: Callable[[], None]) -> bool:
        now = int(self.clock())
        claim_id = str(uuid.uuid4())
        item_key = {
            "pk": {"S": f"IDEMPOTENCY#{key}"},
            "sk": {"S": "STATE"},
        }
        try:
            self._client().update_item(
                TableName=self.table_name,
                Key=item_key,
                UpdateExpression="SET #state = :in_progress, claim_id = :claim_id, expires_at = :lease_end",
                ConditionExpression="attribute_not_exists(pk) OR expires_at <= :now",
                ExpressionAttributeNames={"#state": "state"},
                ExpressionAttributeValues={
                    ":in_progress": {"S": "IN_PROGRESS"},
                    ":claim_id": {"S": claim_id},
                    ":lease_end": {"N": str(now + self.claim_seconds)},
                    ":now": {"N": str(now)},
                },
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
                raise
            existing = self._client().get_item(
                TableName=self.table_name,
                Key=item_key,
                ConsistentRead=True,
            ).get("Item", {})
            if existing.get("state", {}).get("S") == "COMPLETE":
                return False
            raise TransientProcessingError("Idempotency claim is currently in progress") from exc

        action()
        self._client().update_item(
            TableName=self.table_name,
            Key=item_key,
            UpdateExpression="SET #state = :complete, expires_at = :completed_expiry REMOVE claim_id",
            ConditionExpression="claim_id = :claim_id",
            ExpressionAttributeNames={"#state": "state"},
            ExpressionAttributeValues={
                ":complete": {"S": "COMPLETE"},
                ":completed_expiry": {"N": str(now + self.completed_ttl_seconds)},
                ":claim_id": {"S": claim_id},
            },
        )
        return True
