"""Validate a signed GLPI fetch before exposing any deployment credentials."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from automation.change_control import verify_attestation


def main() -> None:
    key = os.environ.get("GMUD_SIGNING_KEY", "").encode()
    encoded = os.environ.get("GMUD_ATTESTATION", "")
    if not key or not encoded:
        raise SystemExit("GMUD signing key and attestation must be configured")
    try:
        evidence = verify_attestation(encoded, key, os.environ["GITHUB_SHA"])
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if str(evidence["change_id"]) != os.environ["GMUD_CHANGE_ID"]:
        raise SystemExit("GMUD input and signed evidence identify different changes")
    if evidence["nonce"] != os.environ["GMUD_REQUEST_NONCE"]:
        raise SystemExit("GMUD request nonce does not match its signed evidence")
    Path("change-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print("GMUD fields were attested for this commit; human approvals remain required.")


if __name__ == "__main__":
    main()
