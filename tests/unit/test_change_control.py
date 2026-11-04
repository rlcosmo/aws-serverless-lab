import base64
import json
from datetime import UTC, datetime, timedelta

import pytest

from automation.change_control import attest_change, validate_change, verify_attestation

NOW = datetime(2026, 11, 4, 12, tzinfo=UTC)
COMMIT = "a" * 40
KEY = b"unit-test-key-only-never-a-real-secret-1234"


def record():
    return {
        "title": "Lab change", "description": "Controlled lab change", "justification": "Test",
        "requester": "technical-test", "owner": "rlcosmo", "environment": "dev",
        "risk": "low", "impact": "lab only", "implementation_plan": "Reviewed image update",
        "rollback_plan": "Restore recorded image digest", "approval_history": [],
        "evidence_links": [], "deployment_requested": True,
        "maintenance_window": {"start": (NOW - timedelta(minutes=1)).isoformat(),
                               "end": (NOW + timedelta(hours=1)).isoformat()},
    }


def test_attestation_contains_metadata_and_is_not_a_human_approval():
    source = record()
    source["description"] = "Private change details must stay in GLPI"
    encoded = attest_change(1, source, COMMIT, KEY, now=NOW)
    decoded = json.loads(base64.urlsafe_b64decode(encoded))
    assert "Private change details" not in str(decoded)
    assert "approval_history" not in decoded["payload"]
    assert verify_attestation(encoded, KEY, COMMIT, now=NOW)["change_id"] == 1


def test_tampered_attestation_is_rejected():
    envelope = json.loads(base64.urlsafe_b64decode(attest_change(1, record(), COMMIT, KEY, now=NOW)))
    envelope["payload"]["change_id"] = 999
    changed = base64.urlsafe_b64encode(json.dumps(envelope).encode()).decode()
    with pytest.raises(ValueError, match="signature"):
        verify_attestation(changed, KEY, COMMIT, now=NOW)


def test_attestation_for_other_commit_or_expired_window_is_rejected():
    encoded = attest_change(1, record(), COMMIT, KEY, now=NOW)
    with pytest.raises(ValueError, match="another commit"):
        verify_attestation(encoded, KEY, "b" * 40, now=NOW)
    with pytest.raises(ValueError, match="expired"):
        verify_attestation(encoded, KEY, COMMIT, now=NOW + timedelta(hours=2))


@pytest.mark.parametrize("missing", ["rollback_plan", "requester", "maintenance_window"])
def test_incomplete_change_cannot_be_attested(missing):
    source = record()
    source.pop(missing)
    with pytest.raises(ValueError, match="mandatory"):
        attest_change(1, source, COMMIT, KEY, now=NOW)


def test_test_records_and_non_dev_changes_cannot_request_deployment():
    source = record()
    source["deployment_requested"] = False
    with pytest.raises(ValueError, match="does not request"):
        validate_change(source, NOW)
    source["deployment_requested"] = True
    source["environment"] = "prod"
    with pytest.raises(ValueError, match="DEV"):
        validate_change(source, NOW)
