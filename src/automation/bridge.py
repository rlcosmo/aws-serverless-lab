"""GLPI OAuth client and GitHub App orchestration for real change evidence."""

from __future__ import annotations

import base64
import html
import json
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlencode, urlsplit

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from automation.change_control import REQUIRED_FIELDS, attest_change


class NoCredentialRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_json(url: str, *, data: Any = None, headers=None, method="GET") -> Any:
    """Bound HTTP calls and keep response bodies and credentials out of errors."""
    request = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.build_opener(NoCredentialRedirect).open(request, timeout=20) as response:
            content = response.read(10 * 1024 * 1024)
            return json.loads(content) if content else None
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Automation HTTP request failed with status {error.code}") from None


class PreformattedRecords(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.parts: list[str] = []
        self.records: list[dict[str, Any]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.active, self.parts = True, []

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "pre" and self.active:
            self.active = False
            try:
                record = json.loads("".join(self.parts))
                if isinstance(record, dict):
                    self.records.append(record)
            except json.JSONDecodeError:
                return


def structured_change(content: str) -> dict[str, Any]:
    parser = PreformattedRecords()
    parser.feed(content)
    matches = [entry for entry in parser.records if REQUIRED_FIELDS <= entry.keys()]
    if len(matches) != 1:
        raise ValueError("GMUD must contain exactly one structured change record in a pre element")
    return matches[0]


class GLPIClient:
    """Use the dedicated OAuth password grant supported by GLPI 12."""

    def __init__(self, credentials: dict[str, Any]) -> None:
        self.credentials = credentials
        self.base = credentials["base_url"].rstrip("/")
        endpoint = urlsplit(self.base)
        allowed = ((endpoint.scheme, endpoint.hostname, endpoint.port) in {
            ("http", "127.0.0.1", 8080), ("http", "glpi", 80), ("http", "glpi", None),
            ("https", "glpi.cosmotechsolutions.com.br", None),
            ("https", "glpi.cosmotechsolutions.com.br", 443),
        })
        if not allowed or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment or endpoint.path:
            raise ValueError("Unexpected GLPI automation endpoint")
        self.token: str | None = None
        self.refresh_at = 0.0

    def _headers(self) -> dict[str, str]:
        if not self.token or time.monotonic() >= self.refresh_at:
            form = {key: self.credentials[key] for key in
                    ("client_id", "client_secret", "username", "password")}
            form.update(grant_type="password", scope="api user")
            result = request_json(self.base + "/api.php/token", data=urlencode(form).encode(),
                                  method="POST")
            self.token = result["access_token"]
            self.refresh_at = time.monotonic() + max(1, int(result.get("expires_in", 3600)) - 60)
        return {"Authorization": "Bearer " + self.token}

    def get_change(self, change_id: int) -> dict[str, Any]:
        if change_id < 1:
            raise ValueError("Invalid change ID")
        return request_json(self.base + f"/api.php/v2/Assistance/Change/{change_id}",
                            headers=self._headers())

    def record_evidence(self, change_id: int, evidence: dict[str, Any]) -> None:
        """Append actual results; never create native human approval records."""
        change = self.get_change(change_id)
        appendix = html.escape(json.dumps({"cosmotech_automation_state": evidence}, sort_keys=True))
        body = json.dumps({"content": change["content"] + f"<pre>{appendix}</pre>"}).encode()
        request_json(self.base + f"/api.php/v2/Assistance/Change/{change_id}", data=body,
                     headers={**self._headers(), "Content-Type": "application/json"}, method="PATCH")


class GitHubAppClient:
    """Mint repository-scoped installation tokens; never reuse personal tokens."""

    repository = "rlcosmo/aws-serverless-lab"

    def __init__(self, credentials: dict[str, Any]) -> None:
        self.credentials = credentials
        self.token: str | None = None
        self.refresh_at = 0.0

    def _headers(self) -> dict[str, str]:
        if not self.token or time.monotonic() >= self.refresh_at:
            def encode(value):
                return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).rstrip(b"=")

            now = int(time.time())
            unsigned = encode({"alg": "RS256", "typ": "JWT"}) + b"." + encode({
                "iat": now - 60, "exp": now + 540, "iss": str(self.credentials["app_id"]),
            })
            private_key = serialization.load_pem_private_key(
                self.credentials["private_key"].encode(), password=None,
            )
            signature = base64.urlsafe_b64encode(private_key.sign(
                unsigned, padding.PKCS1v15(), hashes.SHA256(),
            )).rstrip(b"=")
            jwt = (unsigned + b"." + signature).decode()
            result = request_json(
                f"https://api.github.com/app/installations/{int(self.credentials['installation_id'])}/access_tokens",
                method="POST", headers={"Authorization": "Bearer " + jwt,
                    "Accept": "application/vnd.github+json", "Content-Type": "application/json"},
                data=json.dumps({"repositories": ["aws-serverless-lab"],
                                 "permissions": {"actions": "write", "contents": "read"}}).encode(),
            )
            self.token = result["token"]
            self.refresh_at = time.monotonic() + 3000
        return {"Authorization": "Bearer " + self.token, "Accept": "application/vnd.github+json",
                "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28"}

    def api(self, path: str, *, body=None, method="GET"):
        return request_json(f"https://api.github.com/repos/{self.repository}/{path}",
                            method=method, headers=self._headers(),
                            data=json.dumps(body).encode() if body is not None else None)


def run_change(
    glpi: GLPIClient, github: GitHubAppClient, change_id: int, commit_sha: str, signing_key: bytes,
    *, poll_seconds: int = 60, timeout_seconds: int = 86400,
) -> dict[str, Any]:
    """Fetch, attest, dispatch, wait for real approvals and record actual results."""
    change = glpi.get_change(change_id)
    # Reuse the previously recorded run for this same commit, avoiding duplicate dispatch.
    parser = PreformattedRecords()
    parser.feed(change["content"])
    prior = [entry["cosmotech_automation_state"] for entry in parser.records
             if isinstance(entry.get("cosmotech_automation_state"), dict)
             and entry["cosmotech_automation_state"].get("commit_sha") == commit_sha]
    run_id = next((entry.get("run_id") for entry in reversed(prior) if entry.get("run_id")), None)
    if run_id is None:
        pending = next((entry for entry in reversed(prior) if entry.get("nonce")), None)
        if pending:
            payload = {"nonce": pending["nonce"]}
        else:
            record = structured_change(change["content"])
            if github.api("git/ref/heads/main")["object"]["sha"] != commit_sha:
                raise ValueError("Only the current main commit may be dispatched")
            attestation = attest_change(change_id, record, commit_sha, signing_key)
            payload = json.loads(base64.urlsafe_b64decode(attestation))["payload"]
            # Persist dispatch intent before making the external request. An
            # uncertain dispatch is looked up, never blindly sent again.
            glpi.record_evidence(change_id, {"state": "dispatch_requested", "nonce": payload["nonce"],
                                           "commit_sha": commit_sha})
            github.api("actions/workflows/deploy-dev.yml/dispatches", method="POST", body={
                "ref": "main", "inputs": {"mode": "deploy", "change_id": str(change_id),
                    "attestation": attestation, "request_nonce": payload["nonce"]},
            })
        for _ in range(60):
            runs = github.api("actions/workflows/deploy-dev.yml/runs?event=workflow_dispatch&branch=main&per_page=30")
            match = next((entry for entry in runs["workflow_runs"] if
                          entry["head_sha"] == commit_sha and
                          entry["display_title"].endswith("[" + payload["nonce"] + "]")), None)
            if match:
                run_id = match["id"]
                break
            time.sleep(2)
        if run_id is None:
            raise RuntimeError("Dispatched run not located; inspect workflow history before retrying")
        glpi.record_evidence(change_id, {"state": "waiting_for_real_approvals", "run_id": run_id,
            "nonce": payload["nonce"], "commit_sha": commit_sha,
            "workflow_url": f"https://github.com/{github.repository}/actions/runs/{run_id}"})
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        result = github.api(f"actions/runs/{int(run_id)}")
        if result["head_sha"] != commit_sha or result["path"] != ".github/workflows/deploy-dev.yml":
            raise ValueError("Recorded run does not match the expected deployment workflow and commit")
        if not result["display_title"].startswith(f"DEV deploy GMUD {change_id} ["):
            raise ValueError("Recorded run is not an application deployment for this GMUD")
        if result["status"] == "completed":
            reviews = github.api(f"actions/runs/{int(run_id)}/approvals")
            approved = {env["name"] for item in reviews if item["state"] == "approved"
                        and item["user"]["id"] == 124368446 for env in item["environments"]}
            if result["conclusion"] == "success" and not {"dev", "qa", "po-pm", "infra-sre"} <= approved:
                raise ValueError("Successful deployment lacks the four real approvals")
            evidence = {"state": result["conclusion"], "run_id": run_id, "commit_sha": commit_sha,
                "workflow_url": result["html_url"], "observed_at": datetime.now(UTC).isoformat(),
                "real_reviews": [{"state": item["state"], "user_id": item["user"]["id"],
                    "environments": [env["name"] for env in item["environments"]]} for item in reviews]}
            glpi.record_evidence(change_id, evidence)
            return evidence
        time.sleep(poll_seconds)
    raise TimeoutError("Workflow remains pending; resume polling the same run, do not simulate approval")
