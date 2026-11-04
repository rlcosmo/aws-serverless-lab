#!/bin/bash
set -Eeuo pipefail
umask 077
run_id="$(date -u +%Y%m%dT%H%M%SZ)"
backup_dir="/opt/cosmotech/backups/$run_id"
[ ! -e "$backup_dir" ] || { echo "Backup directory already exists" >&2; exit 1; }
glpi_restore="cosmotech-glpi-restore-$run_id"
kestra_restore="cosmotech-kestra-restore-$run_id"
install -d -m 700 "$backup_dir"
glpi_db=$(docker ps -q --filter label=com.docker.compose.service=glpi-db)
kestra_db=$(docker ps -q --filter label=com.docker.compose.service=kestra-db)
trap 'docker stop "$glpi_restore" "$kestra_restore" >/dev/null 2>&1 || true' EXIT
date -u +%FT%TZ > "$backup_dir/started.txt"
docker exec "$glpi_db" sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" exec mariadb-dump -uroot --single-transaction --routines --triggers --events glpi' > "$backup_dir/glpi.sql"
docker exec "$kestra_db" sh -c 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup_dir/kestra.dump"
tar -C /opt/cosmotech -czf "$backup_dir/reconstruction.tar.gz" itsm/application.yaml secrets/itsm/runtime.env aws-serverless-lab/ops/itsm
sha256sum "$backup_dir/glpi.sql" "$backup_dir/kestra.dump" "$backup_dir/reconstruction.tar.gz" > "$backup_dir/SHA256SUMS"
# Isolated restore containers: no published ports, no network and distinct volumes.
if docker container inspect "$glpi_restore" >/dev/null 2>&1 || docker container inspect "$kestra_restore" >/dev/null 2>&1; then
  echo 'Restore container already exists; refusing to overwrite it.' >&2
  exit 1
fi
restore_password=$(openssl rand -hex 32)
printf 'MARIADB_ROOT_PASSWORD=%s\n' "$restore_password" > "$backup_dir/mariadb-restore.env"
printf 'POSTGRES_PASSWORD=%s\nPOSTGRES_DB=kestra\nPOSTGRES_USER=kestra\n' "$restore_password" > "$backup_dir/postgres-restore.env"
unset restore_password
docker run -d --name "$glpi_restore" --network none --memory 1g --cpus 1 --env-file "$backup_dir/mariadb-restore.env" --mount type=volume,source=cosmotech-glpi-restore-$run_id,target=/var/lib/mysql mariadb@sha256:d1891ede5a559f1086f55053bb8cc1569b0298338c4d72d71725a7f74f6ba620 >/dev/null
docker run -d --name "$kestra_restore" --network none --memory 512m --cpus 1 --env-file "$backup_dir/postgres-restore.env" --mount type=volume,source=cosmotech-kestra-restore-$run_id,target=/var/lib/postgresql/data postgres@sha256:266d3c257594e195b309ae9d1805e54c788f1d7b375f56bf6c367aac6c917e7b >/dev/null
for n in $(seq 1 60); do
 if docker exec "$glpi_restore" healthcheck.sh --connect --innodb_initialized >/dev/null 2>&1 && docker exec "$kestra_restore" pg_isready -U kestra -d kestra >/dev/null 2>&1; then break; fi
 sleep 2
done
docker exec "$glpi_restore" sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" exec mariadb -uroot -e "CREATE DATABASE glpi;"'
docker exec -i "$glpi_restore" sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" exec mariadb -uroot glpi' < "$backup_dir/glpi.sql"
docker exec -i "$kestra_restore" pg_restore -U kestra -d kestra --exit-on-error < "$backup_dir/kestra.dump"
docker exec "$glpi_restore" sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" exec mariadb-check -uroot --check glpi' > "$backup_dir/mariadb-check.txt"
docker exec "$glpi_restore" sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" exec mariadb -uroot glpi -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE(); SELECT COUNT(*) FROM glpi_tickets; SELECT COUNT(*) FROM glpi_changes;"' > "$backup_dir/glpi-restored-counts.txt"
docker exec "$kestra_restore" psql -U kestra -d kestra -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';" > "$backup_dir/kestra-restored-table-count.txt"
date -u +%FT%TZ > "$backup_dir/finished.txt"
# Stop only the isolated test containers; retain restored volumes and evidence.
docker stop "$glpi_restore" "$kestra_restore" >/dev/null
printf 'Logical backup and isolated restores completed.\n'
cat "$backup_dir/started.txt" "$backup_dir/finished.txt"
printf 'GLPI restored counts (tables/tickets/changes):\n'; cat "$backup_dir/glpi-restored-counts.txt"
printf 'Kestra restored public tables:\n'; cat "$backup_dir/kestra-restored-table-count.txt"
printf 'MariaDB table check errors: '; grep -cE 'error|corrupt' "$backup_dir/mariadb-check.txt" || true
