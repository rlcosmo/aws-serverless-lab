"""Kestra entry point using technical SSM credentials and a GitHub App."""

import json
import os
import sys
from pathlib import Path

import boto3
from botocore.config import Config

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from automation.bridge import GitHubAppClient, GLPIClient, run_change


def main() -> None:
    client = boto3.client("ssm", region_name=os.getenv("AWS_REGION", "us-east-1"),
        config=Config(connect_timeout=2, read_timeout=3,
                      retries={"total_max_attempts": 3, "mode": "standard"}))

    def parameter(name):
        return client.get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]

    glpi_credentials = json.loads(parameter("/cosmotech/itsm/glpi/automation-credentials"))
    # Docker task containers use the shared ITSM Docker network, not host loopback.
    if os.getenv("GLPI_AUTOMATION_BASE_URL"):
        glpi_credentials["base_url"] = os.environ["GLPI_AUTOMATION_BASE_URL"]
    github_credentials = json.loads(parameter("/cosmotech/itsm/github/automation-app"))
    key = parameter("/cosmotech/itsm/automation/gmud-signing-key").encode()
    result = run_change(GLPIClient(glpi_credentials), GitHubAppClient(github_credentials),
                        int(os.environ["GMUD_CHANGE_ID"]), os.environ["GMUD_COMMIT_SHA"], key)
    print(json.dumps({"change_id": int(os.environ["GMUD_CHANGE_ID"]),
                      "run_id": result["run_id"], "state": result["state"]}))


if __name__ == "__main__":
    main()
