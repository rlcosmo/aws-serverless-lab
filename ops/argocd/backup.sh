#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
exec 9>/run/lock/cosmotech-argocd-backup.lock
flock -n 9 || exit 1
run_dir="/opt/cosmotech/backups/argocd/$(date -u +%Y%m%dT%H%M%SZ)"
install -d -m 0700 "$run_dir"
python3 - "$run_dir" <<'PY'
import sqlite3,sys
from pathlib import Path
with sqlite3.connect('file:/var/lib/rancher/k3s/server/db/state.db?mode=ro', uri=True) as source:
    with sqlite3.connect(str(Path(sys.argv[1])/'state.db')) as target:
        source.backup(target)
        assert target.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
PY
tar -czf "$run_dir/config.tar.gz" /etc/rancher/k3s /var/lib/rancher/k3s/server/token /var/lib/rancher/k3s/server/cred/encryption-config.json 2>/dev/null
(cd "$run_dir" && sha256sum state.db config.tar.gz > SHA256SUMS && sha256sum -c SHA256SUMS)
# Daily encrypted EC2 backup captures this root-only directory; cleanup is manual.
