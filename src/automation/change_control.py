"""Validate GLPI changes and authenticate deployment attestations."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

REQUIRED_FIELDS = {
    "title", "description", "justification", "requester", "owner", "environment",
    "risk", "impact", "implementation_plan", "rollback_plan", "maintenance_window",
    "approval_history", "evidence_links",
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def validate_change(record: dict[str, Any], now: datetime) -> datetime:
    """Validate a real fetched record; this does not approve the change."""
    if REQUIRED_FIELDS - record.keys():
        raise ValueError("GMUD is missing mandatory fields")
    for field in REQUIRED_FIELDS - {"approval_history", "evidence_links", "maintenance_window"}:
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError("GMUD has an empty mandatory field")
    if record["environment"] != "dev" or record.get("deployment_requested") is not True:
        raise ValueError("GMUD does not request a DEV deployment")
    if not isinstance(record["approval_history"], list) or not isinstance(record["evidence_links"], list):
        raise TypeError("GMUD evidence and approval history must be lists")
    window = record["maintenance_window"]
    if not isinstance(window, dict):
        raise TypeError("GMUD maintenance window is invalid")
    if not {"start", "end"} <= window.keys():
        raise ValueError("GMUD maintenance window is incomplete")
    start, end = (datetime.fromisoformat(window[key]) for key in ("start", "end"))
    if start.tzinfo is None or end.tzinfo is None or not start <= now < end:
        raise ValueError("GMUD is outside its maintenance window")
    return end


def attest_change(
    change_id: int, record: dict[str, Any], commit_sha: str, key: bytes,
    *, now: datetime | None = None,
) -> str:
    """Sign public metadata after validating the fetched GLPI record."""
    now = now or datetime.now(UTC)
    end = validate_change(record, now)
    if change_id < 1 or not re.fullmatch(r"[a-f0-9]{40}", commit_sha) or len(key) < 32:
        raise ValueError("Invalid attestation parameters")
    payload = {
        "change_id": change_id, "commit_sha": commit_sha, "environment": "dev",
        "record_sha256": hashlib.sha256(canonical(record)).hexdigest(),
        "issued_at": now.isoformat(), "expires_at": min(end, now + timedelta(hours=24)).isoformat(),
        "nonce": secrets.token_hex(16),
    }
    signature = hmac.new(key, canonical(payload), hashlib.sha256).hexdigest()
    # No ticket body, user password or API token is sent to the public workflow.
    return base64.urlsafe_b64encode(canonical({"payload": payload, "signature": signature})).decode()


def verify_attestation(
    encoded: str, key: bytes, expected_commit: str, *, now: datetime | None = None,
) -> dict[str, Any]:
    """Reject tampering, stale windows and evidence for another commit."""
    now = now or datetime.now(UTC)
    if len(encoded) > 8192 or len(key) < 32:
        raise ValueError("Invalid attestation")
    try:
        envelope = json.loads(base64.b64decode(encoded, altchars=b"-_", validate=True))
        payload, signature = envelope["payload"], envelope["signature"]
        expected = hmac.new(key, canonical(payload), hashlib.sha256).hexdigest()
        if not isinstance(signature, str) or not hmac.compare_digest(signature, expected):
            raise ValueError("GMUD attestation signature is invalid")
        issued = datetime.fromisoformat(payload["issued_at"])
        expires = datetime.fromisoformat(payload["expires_at"])
        if issued.tzinfo is None or expires.tzinfo is None:
            raise ValueError("GMUD attestation timestamps require a timezone")
        if issued > now + timedelta(minutes=5) or not now < expires <= issued + timedelta(hours=24):
            raise ValueError("GMUD attestation has expired or has an invalid window")
        if payload["commit_sha"] != expected_commit or payload["environment"] != "dev":
            raise ValueError("GMUD attestation targets another commit or environment")
        if type(payload["change_id"]) is not int or payload["change_id"] < 1:
            raise ValueError("GMUD ID is invalid")
        return payload
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("Malformed GMUD attestation") from error
