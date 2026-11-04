#!/usr/bin/env bash
set -Eeuo pipefail
job="${1:?backup job name required}"
[[ "$job" == Logical || "$job" == Tempo ]] || exit 2
value=1
[[ "${SERVICE_RESULT:-unknown}" != success ]] || value=0
# Status only: database contents, credentials and raw errors are never exported.
aws cloudwatch put-metric-data --region us-east-1 --namespace CosmoTech/Backups \
  --metric-data "MetricName=JobFailure,Dimensions=[{Name=JobName,Value=$job}],Value=$value,Unit=Count"
