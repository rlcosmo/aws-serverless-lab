"""DynamoDB-backed idempotency claim with lease-based recovery."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import Any

from boto3.dynamodb.conditions import Attr

from orders.consumer.errors import TransientProcessingError
from orders.consumer.repository import create_dynamodb_resource

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
        dynamodb_resource: Any | None = None,
        clock: Callable[[], float] = time.time,
        claim_seconds: int = DEFAULT_CLAIM_SECONDS,
        completed_ttl_seconds: int = DEFAULT_COMPLETED_TTL_SECONDS,
    ) -> None:
        if not table_name:
            raise ValueError("table_name must not be empty")
        self.table_name = table_name
        self.resource = dynamodb_resource
        self.clock = clock
        self.claim_seconds = claim_seconds
        self.completed_ttl_seconds = completed_ttl_seconds
        self._table: Any | None = None

    def _get_table(self) -> Any:
        if self._table is None:
            resource = self.resource or create_dynamodb_resource()
            self._table = resource.Table(self.table_name)
        return self._table

    def execute_once(self, key: str, action: Callable[[], None]) -> bool:
        now = int(self.clock())
        claim_id = str(uuid.uuid4())
        item_key = {"pk": f"IDEMPOTENCY#V2#{key}", "sk": "STATE"}
        table = self._get_table()
        try:
            table.update_item(
                Key=item_key,
                UpdateExpression="SET #state = :in_progress, claim_id = :claim_id, expires_at = :lease_end",
                ConditionExpression=Attr("pk").not_exists() | Attr("expires_at").lte(now),
                ExpressionAttributeNames={"#state": "state"},
                ExpressionAttributeValues={
                    ":in_progress": "IN_PROGRESS",
                    ":claim_id": claim_id,
                    ":lease_end": now + self.claim_seconds,
                },
            )
        except table.meta.client.exceptions.ConditionalCheckFailedException as exc:
            existing = table.get_item(
                Key=item_key,
                ConsistentRead=True,
            ).get("Item", {})
            if existing.get("state") == "COMPLETE":
                return False
            raise TransientProcessingError("Idempotency claim is currently in progress") from exc

        action()
        table.update_item(
            Key=item_key,
            UpdateExpression="SET #state = :complete, expires_at = :completed_expiry REMOVE claim_id",
            ConditionExpression=Attr("claim_id").eq(claim_id),
            ExpressionAttributeNames={"#state": "state"},
            ExpressionAttributeValues={
                ":complete": "COMPLETE",
                ":completed_expiry": now + self.completed_ttl_seconds,
            },
        )
        return True
