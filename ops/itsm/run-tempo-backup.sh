#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
export AWS_DEFAULT_REGION=us-east-1
export KUBECONFIG=/opt/cosmotech/backup-operations/tempo-kubeconfig
marker=/opt/cosmotech/backup-operations/tempo-resume-required
if [[ "${1:-}" == resume ]]; then
  if [[ -f "$marker" ]]; then
    kubectl scale sts/tempo -n observability --replicas=1
    kubectl rollout status sts/tempo -n observability --timeout=120s
    rm -f "$marker"
  fi
  exit 0
fi
exec 9>/run/lock/cosmotech-tempo-backup.lock
flock -n 9 || exit 1
aws eks update-kubeconfig --region us-east-1 --name aws-eks-istio-lab-dev --kubeconfig "$KUBECONFIG" >/dev/null
run_id="$(date -u +%Y%m%dT%H%M%SZ)"
install -d -m 0700 /opt/cosmotech/backups/tempo
python3 /opt/cosmotech/backup-operations/backup_tempo_consistently.py \
  --resume-marker "$marker" --evidence "/opt/cosmotech/backups/tempo/$run_id.json"
