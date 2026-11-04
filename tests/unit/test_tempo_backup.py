"""Maintenance must resume Tempo after backup failures and reject unsafe starts."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "tempo_backup", Path(__file__).parents[2] / "scripts/backup_tempo_consistently.py",
)
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


def setup_commands(monkeypatch, tmp_path, *, replicas=1, fail=False):
    calls = []

    def json_command(arguments):
        if arguments[1:3] == ["sts", "get-caller-identity"]:
            return {"Account": "414053644145", "Arn": "arn:aws:sts::414053644145:assumed-role/lab/test"}
        if arguments[1:3] == ["get", "sts"]:
            return {"spec": {"replicas": replicas}}
        if arguments[1:3] == ["get", "pvc"]:
            return {"spec": {"volumeName": "tempo-volume"}}
        if arguments[1:3] == ["get", "pv"]:
            return {"spec": {"csi": {"driver": "ebs.csi.aws.com", "volumeHandle": "vol-test"}}}
        if arguments[1:3] == ["ec2", "describe-volumes"]:
            return {"Volumes": [{"Encrypted": True}]}
        if arguments[1:3] == ["backup", "start-backup-job"]:
            if fail:
                raise RuntimeError("Controlled backup failure")
            return {"BackupJobId": "test-backup"}
        if arguments[1:3] == ["backup", "describe-backup-job"]:
            return {"State": "RUNNING", "RecoveryPointArn": "arn:aws:ec2:region:account:snapshot/snap-test"}
        raise AssertionError(arguments)

    def run(arguments, **kwargs):
        calls.append(arguments)
        return subprocess.CompletedProcess(arguments, 0, json.dumps({"Snapshots": [{"State": "pending"}]}))

    monkeypatch.setattr(backup, "json_command", json_command)
    monkeypatch.setattr(backup.subprocess, "run", run)
    monkeypatch.setattr(sys, "argv", ["backup", "--evidence", str(tmp_path / "evidence.json"),
                                     "--resume-marker", str(tmp_path / "resume-required")])
    return calls


def test_failed_backup_resumes_original_tempo_and_preserves_resume_marker(monkeypatch, tmp_path):
    calls = setup_commands(monkeypatch, tmp_path, fail=True)
    with pytest.raises(RuntimeError, match="Controlled backup failure"):
        backup.main()
    scales = [call[-1] for call in calls if call[1] == "scale"]
    assert scales == ["--replicas=0", "--replicas=1"]
    assert (tmp_path / "resume-required").exists()
    assert json.loads((tmp_path / "evidence.json").read_text())["write_quiescence_seconds"] >= 0


def test_existing_maintenance_is_not_overridden(monkeypatch, tmp_path):
    calls = setup_commands(monkeypatch, tmp_path, replicas=0)
    with pytest.raises(SystemExit, match="exactly one replica"):
        backup.main()
    assert calls == []
    assert not (tmp_path / "resume-required").exists()


def test_snapshot_cut_resumes_and_records_readiness(monkeypatch, tmp_path):
    calls = setup_commands(monkeypatch, tmp_path)
    backup.main()
    evidence = json.loads((tmp_path / "evidence.json").read_text())
    assert evidence["backup_job_id"] == "test-backup"
    assert evidence["snapshot_id"] == "snap-test"
    assert evidence["ready_elapsed_seconds"] >= evidence["write_quiescence_seconds"]
    assert calls[-1][1:3] == ["rollout", "status"]
    assert not (tmp_path / "resume-required").exists()
