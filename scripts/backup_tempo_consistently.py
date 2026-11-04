"""Quiesce only Tempo, establish an EBS snapshot cut, and always resume it."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
import uuid
from pathlib import Path


def json_command(arguments: list[str]) -> dict:
    return json.loads(subprocess.check_output(arguments))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=Path("dist/tempo-backup-evidence.json"))
    parser.add_argument("--resume-marker", type=Path)
    args = parser.parse_args()
    caller = json_command(["aws", "sts", "get-caller-identity", "--output", "json"])
    if caller["Account"] != "414053644145" or ":assumed-role/" not in caller["Arn"]:
        raise SystemExit("An authorized short-lived role session in the lab account is required")
    statefulset = json_command(["kubectl", "get", "sts", "tempo", "-n", "observability", "-o", "json"])
    if statefulset["spec"]["replicas"] != 1:
        raise SystemExit("Tempo must have exactly one replica before this maintenance operation")
    claim = json_command(["kubectl", "get", "pvc", "storage-tempo-0", "-n", "observability", "-o", "json"])
    volume = json_command(["kubectl", "get", "pv", claim["spec"]["volumeName"], "-o", "json"])
    if volume["spec"].get("csi", {}).get("driver") != "ebs.csi.aws.com":
        raise SystemExit("Tempo must already use a persistent EBS CSI volume")
    volume_id = volume["spec"]["csi"]["volumeHandle"]
    ec2_volume = json_command(["aws", "ec2", "describe-volumes", "--volume-ids", volume_id,
                              "--output", "json"])["Volumes"][0]
    if not ec2_volume["Encrypted"]:
        raise SystemExit("Expected an encrypted application volume")
    evidence = {"volume_id": volume_id, "caller_role": caller["Arn"]}
    started = time.monotonic()
    if args.resume_marker:
        args.resume_marker.write_text("Resume the original Tempo replica after this backup operation.\n")
    try:
        subprocess.run(["kubectl", "scale", "sts/tempo", "-n", "observability", "--replicas=0"], check=True)
        subprocess.run(["kubectl", "wait", "--for=delete", "pod/tempo-0", "-n", "observability",
                        "--timeout=120s"], check=True)
        job = json_command(["aws", "backup", "start-backup-job", "--backup-vault-name",
            "cosmotech-itsm-dev-vault", "--resource-arn",
            f"arn:aws:ec2:us-east-1:414053644145:volume/{volume_id}", "--iam-role-arn",
            "arn:aws:iam::414053644145:role/cosmotech-itsm-dev-backup-role", "--lifecycle",
            "DeleteAfterDays=14", "--idempotency-token", "tempo-quiesced-" + uuid.uuid4().hex,
            "--output", "json"])
        evidence["backup_job_id"] = job["BackupJobId"]
        for _ in range(80):
            state = json_command(["aws", "backup", "describe-backup-job", "--backup-job-id",
                                  job["BackupJobId"], "--output", "json"])
            if state["State"] in {"FAILED", "ABORTED", "EXPIRED"}:
                raise RuntimeError("Backup failed during maintenance")
            arn = state.get("RecoveryPointArn", "")
            if ":snapshot/" in arn:
                snapshot_id = arn.split("/")[-1]
                snapshot = subprocess.run(["aws", "ec2", "describe-snapshots", "--snapshot-ids",
                    snapshot_id, "--output", "json"], check=False, capture_output=True, text=True)
                if snapshot.returncode == 0 and json.loads(snapshot.stdout)["Snapshots"][0]["State"] in {
                    "pending", "completed",
                }:
                    evidence["snapshot_id"] = snapshot_id
                    break
            time.sleep(3)
        else:
            raise TimeoutError("No snapshot cut was observed in the bounded maintenance window")
    finally:
        subprocess.run(["kubectl", "scale", "sts/tempo", "-n", "observability", "--replicas=1"], check=True)
        evidence["write_quiescence_seconds"] = round(time.monotonic() - started, 2)
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(evidence, indent=2) + "\n")
    subprocess.run(["kubectl", "rollout", "status", "sts/tempo", "-n", "observability",
                    "--timeout=120s"], check=True)
    if args.resume_marker:
        args.resume_marker.unlink(missing_ok=True)
    evidence["ready_elapsed_seconds"] = round(time.monotonic() - started, 2)
    args.evidence.write_text(json.dumps(evidence, indent=2) + "\n")
    print("Tempo resumed; backup job and timing evidence recorded. Verify backup completion separately.")


if __name__ == "__main__":
    main()
