#!/usr/bin/env bash
# Consistent logical dumps before the existing daily 05:00 UTC EC2 backup.
set -Eeuo pipefail
umask 077
exec 9>/run/lock/cosmotech-logical-backup.lock
flock -n 9 || { echo 'Another logical backup is running'; exit 1; }
run_id="$(date -u +%Y%m%dT%H%M%SZ)"
backup_dir="/opt/cosmotech/backups/logical/$run_id"
[[ ! -e "$backup_dir" ]] || exit 1
install -d -m 0700 "$backup_dir"
trap 'echo "Logical backup failed; incomplete capture retained for investigation" >&2' ERR
glpi_db="$(docker ps -q --filter label=com.docker.compose.service=glpi-db)"
kestra_db="$(docker ps -q --filter label=com.docker.compose.service=kestra-db)"
[[ -n "$glpi_db" && -n "$kestra_db" ]] || exit 1
date -u +%FT%TZ > "$backup_dir/started.txt"
docker exec "$glpi_db" sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" exec mariadb-dump -uroot --single-transaction --routines --triggers --events glpi' > "$backup_dir/glpi.sql"
docker exec "$kestra_db" sh -c 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup_dir/kestra.dump"
automation_db="$(docker ps -q --filter label=com.docker.compose.project=cosmotech-automation --filter label=com.docker.compose.service=database)"
if [[ -n "$automation_db" ]]; then
  docker exec "$automation_db" sh -c 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup_dir/kestra-automation.dump"
  docker exec -i "$automation_db" pg_restore --list < "$backup_dir/kestra-automation.dump" > "$backup_dir/automation-postgres-toc.txt"
fi
# Keep reconstruction settings and technical credentials encrypted at rest by EBS.
# Archive stays root-only and is included in the encrypted EC2 recovery point.
[[ ! -d /opt/cosmotech/itsm-automation ]] || automation_config=itsm-automation
config_paths=(itsm/application.yaml secrets/itsm/runtime.env aws-serverless-lab/ops/itsm)
[[ -z "${automation_config:-}" ]] || config_paths+=("$automation_config")
[[ ! -d /opt/cosmotech/secrets/automation ]] || config_paths+=(secrets/automation)
[[ ! -d /etc/nginx ]] || config_paths+=(/etc/nginx)
tar -C /opt/cosmotech -czf "$backup_dir/reconstruction.tar.gz" "${config_paths[@]}" 2> "$backup_dir/archive-warnings.txt"
[[ -s "$backup_dir/glpi.sql" && -s "$backup_dir/kestra.dump" && -s "$backup_dir/reconstruction.tar.gz" ]]
docker exec -i "$kestra_db" pg_restore --list < "$backup_dir/kestra.dump" > "$backup_dir/postgres-toc.txt"
(cd "$backup_dir" && sha256sum glpi.sql *.dump reconstruction.tar.gz > SHA256SUMS && sha256sum --check SHA256SUMS >/dev/null)
date -u +%FT%TZ > "$backup_dir/finished.txt"
printf '%s\n' "$run_id" > "$backup_dir/COMPLETE"
printf 'Consistent logical dumps and protected reconstruction archive completed: %s\n' "$run_id"
# No automatic deletion: retain prior captures until a retention cleanup is reviewed.
