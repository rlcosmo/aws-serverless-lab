"""Fail closed if the four real GitHub reviewer protections are missing."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

REPOSITORY = "rlcosmo/aws-serverless-lab"
ENVIRONMENTS = ("dev", "qa", "po-pm", "infra-sre")
REVIEWER_ID = 124368446


def api(path: str):
    return json.loads(subprocess.check_output(["gh", "api", f"repos/{REPOSITORY}/{path}"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-run-reviews", action="store_true")
    args = parser.parse_args()
    evidence = []
    for name in ENVIRONMENTS:
        environment = api(f"environments/{name}")
        rules = environment.get("protection_rules", [])
        reviewers = [entry for rule in rules if rule["type"] == "required_reviewers"
                     for entry in rule.get("reviewers", [])]
        if not reviewers or any(entry["type"] != "User" or
                               entry["reviewer"]["id"] != REVIEWER_ID for entry in reviewers):
            raise SystemExit(f"{name}: required real reviewer is missing or unexpected")
        if environment.get("can_admins_bypass") is not False:
            raise SystemExit(f"{name}: administrator bypass must be disabled")
        policies = api(f"environments/{name}/deployment-branch-policies")["branch_policies"]
        if len(policies) != 1 or policies[0]["name"] != "main" or policies[0]["type"] != "branch":
            raise SystemExit(f"{name}: deployment must be restricted to main")
        evidence.append({"environment": name, "required_reviewer_id": REVIEWER_ID,
                         "admin_bypass": False, "branch": "main"})
    if args.verify_run_reviews:
        reviews = api(f"actions/runs/{os.environ['GITHUB_RUN_ID']}/approvals")
        approved = set()
        for review in reviews:
            if review["state"] == "approved" and review["user"]["id"] == REVIEWER_ID:
                approved.update(entry["name"] for entry in review["environments"])
        if not set(ENVIRONMENTS) <= approved:
            raise SystemExit("Four real approvals for this exact workflow run are required")
        evidence.append({"run_id": os.environ["GITHUB_RUN_ID"],
                         "approved_environments": sorted(approved), "reviewer_id": REVIEWER_ID})
    Path("approval-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("All four protected environments have the expected real reviewer configuration.")


if __name__ == "__main__":
    main()
