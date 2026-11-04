#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
free -m
docker ps --format "{{.Names}} {{.Status}}"
journalctl -u cosmotech-tempo-backup.service -n 35 --no-pager || true
[[ "$EUID" == 0 ]] || exit 1
for executable in docker flock systemctl tar sha256sum aws kubectl python3; do command -v "$executable" >/dev/null; done
install -d -m 0700 /root/snap /opt/cosmotech/backup-operations
install -m 0700 "$source_dir/publish-backup-status.sh" /opt/cosmotech/backup-operations/publish-backup-status.sh
install -m 0700 "$source_dir/backup-logical.sh" /opt/cosmotech/backup-operations/backup-logical.sh
install -m 0644 "$source_dir/systemd/cosmotech-logical-backup.service" /etc/systemd/system/
install -m 0644 "$source_dir/systemd/cosmotech-logical-backup.timer" /etc/systemd/system/
install -m 0700 "$source_dir/run-tempo-backup.sh" /opt/cosmotech/backup-operations/run-tempo-backup.sh
install -m 0700 "$source_dir/backup_tempo_consistently.py" /opt/cosmotech/backup-operations/backup_tempo_consistently.py
install -m 0644 "$source_dir/systemd/cosmotech-tempo-backup.service" /etc/systemd/system/
install -m 0644 "$source_dir/systemd/cosmotech-tempo-backup.timer" /etc/systemd/system/
systemd-analyze verify /etc/systemd/system/cosmotech-tempo-backup.service /etc/systemd/system/cosmotech-tempo-backup.timer
systemd-analyze verify /etc/systemd/system/cosmotech-logical-backup.service /etc/systemd/system/cosmotech-logical-backup.timer
systemctl daemon-reload
systemctl enable cosmotech-logical-backup.timer >/dev/null
# Run once before enabling the schedule to validate actual database access.
systemctl start cosmotech-logical-backup.service
systemctl start cosmotech-logical-backup.timer
systemctl is-active cosmotech-logical-backup.timer
systemctl show cosmotech-logical-backup.service --property=Result --property=ExecMainStatus
systemctl list-timers cosmotech-logical-backup.timer --no-pager

systemctl enable --now cosmotech-tempo-backup.timer >/dev/null
# Re-installing monitoring must not pause a healthy Tempo a second time.
if [[ "$(systemctl show cosmotech-tempo-backup.service --value --property=Result)" == success ]] &&
   [[ "$(systemctl show cosmotech-tempo-backup.service --value --property=ExecMainStartTimestampMonotonic)" != 0 ]]; then
  SERVICE_RESULT=success /opt/cosmotech/backup-operations/publish-backup-status.sh Tempo
else
  systemctl start cosmotech-tempo-backup.service
fi
systemctl show cosmotech-tempo-backup.service --property=Result --property=ExecMainStatus
systemctl list-timers cosmotech-tempo-backup.timer --no-pager
