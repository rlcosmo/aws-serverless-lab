"""Validate only the dedicated loopback Kestra instance using its own credential."""

from __future__ import annotations

import base64
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path("/opt/cosmotech/automation-source")
SECRET = Path("/opt/cosmotech/secrets/automation/kestra-oss/credentials.json")
EVIDENCE = Path("/opt/cosmotech/backups/kestra-automation-functional.json")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main() -> None:
    credentials = json.loads(SECRET.read_text())
    if credentials["base_url"] != "http://127.0.0.1:8082":
        raise SystemExit("Refusing to use credentials outside the dedicated instance")
    token = base64.b64encode(
        (credentials["username"] + ":" + credentials["password"]).encode(),
    ).decode()
    opener = urllib.request.build_opener(NoRedirect)

    def request(path, *, data=None, method="GET", authenticated=True, content_type=None):
        headers = {"Authorization": "Basic " + token} if authenticated else {}
        if content_type:
            headers["Content-Type"] = content_type
        req = urllib.request.Request(credentials["base_url"] + path, data=data,
                                     method=method, headers=headers)
        try:
            with opener.open(req, timeout=15) as response:
                raw = response.read(5 * 1024 * 1024)
                return response.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            return error.code, None
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            return 0, None

    for _ in range(120):
        status, _ = request("/api/v1/main/flows/search")
        if status == 200:
            break
        time.sleep(2)
    else:
        raise SystemExit("Dedicated Kestra authenticated readiness did not pass")
    anonymous, _ = request("/api/v1/main/flows/search", authenticated=False)
    if anonymous != 401:
        raise SystemExit("Dedicated Kestra must reject anonymous API access")
    source = (ROOT / "functional-flow.yaml").read_bytes()
    path = "/api/v1/main/flows/cosmotech.automation/cosmotech_private_functional_test"
    status, _ = request(path)
    if status == 404:
        status, _ = request("/api/v1/main/flows", data=source, method="POST",
                            content_type="application/x-yaml")
    elif status == 200:
        status, _ = request(path, data=source, method="PUT", content_type="application/x-yaml")
    if status not in {200, 201}:
        raise SystemExit(f"Dedicated functional flow creation failed: HTTP {status}")
    boundary = "cosmotech-empty-form"
    status, execution = request(
        "/api/v1/main/executions/cosmotech.automation/cosmotech_private_functional_test",
        data=("--" + boundary + "--\r\n").encode(), method="POST",
        content_type="multipart/form-data; boundary=" + boundary,
    )
    if status not in {200, 201}:
        raise SystemExit(f"Dedicated execution creation failed: HTTP {status}")
    execution_id = execution["id"]
    for _ in range(120):
        status, execution = request("/api/v1/main/executions/" + execution_id)
        state = execution.get("state", {}).get("current") if execution else None
        if state in {"SUCCESS", "WARNING", "FAILED", "KILLED", "CANCELLED"}:
            break
        time.sleep(2)
    else:
        raise SystemExit("Dedicated functional execution exceeded its bounded wait")
    log_status, logs = request("/api/v1/main/logs/" + execution_id)
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    evidence = {"execution_id": execution_id, "state": state,
                "anonymous_api_status": anonymous, "logs_status": log_status,
                "logs_present": bool(logs), "personal_engine_modified": False}
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n")
    EVIDENCE.chmod(0o600)
    if state != "SUCCESS" or log_status != 200 or not logs:
        # Save private logs for diagnosis; never print credential-bearing bodies.
        (EVIDENCE.parent / "kestra-automation-private-logs.json").write_text(json.dumps(logs))
        raise SystemExit(f"Functional workflow did not pass: {state}; private evidence saved")
    before = subprocess.check_output(["docker", "ps", "-q",
        "--filter", "label=com.docker.compose.project=cosmotech-automation",
        "--filter", "label=com.docker.compose.service=engine"], text=True).strip()
    subprocess.run(["docker", "restart", before], check=True, capture_output=True)
    for _ in range(120):
        status, restored = request("/api/v1/main/executions/" + execution_id)
        if status == 200 and restored.get("state", {}).get("current") == "SUCCESS":
            evidence["restart_persistence"] = "passed"
            break
        time.sleep(2)
    else:
        raise SystemExit("Dedicated execution did not persist across restart")
    EVIDENCE.write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence))


if __name__ == "__main__":
    main()
