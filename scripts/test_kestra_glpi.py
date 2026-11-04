"""Read and annotate only the existing isolated GLPI test GMUD from Kestra."""

from __future__ import annotations

import json
import os

import boto3
from botocore.config import Config

from automation.bridge import GLPIClient


def main() -> None:
    ssm = boto3.client("ssm", region_name="us-east-1", config=Config(
        connect_timeout=2, read_timeout=3,
        retries={"total_max_attempts": 3, "mode": "standard"},
    ))
    credentials = json.loads(ssm.get_parameter(
        Name="/cosmotech/itsm/glpi/automation-credentials", WithDecryption=True,
    )["Parameter"]["Value"])
    glpi = GLPIClient(credentials)
    change = glpi.get_change(1)
    if not change.get("name", "").startswith("[COSMOTECH LAB TEST]"):
        raise RuntimeError("Expected the isolated lab test GMUD; no record was changed")
    execution_id = os.environ.get("KESTRA_EXECUTION_ID", "")
    if not execution_id or not execution_id.isalnum():
        raise RuntimeError("A real Kestra execution ID is required")
    glpi.record_evidence(1, {"kind": "kestra-functional-test", "execution_id": execution_id,
                           "state": "SUCCESS", "synthetic": True})
    print(json.dumps({"change_id": 1, "execution_id": execution_id,
                      "technical_auth": "passed", "evidence_update": "passed"}))


if __name__ == "__main__":
    main()
