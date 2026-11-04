#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
credential_file=/opt/cosmotech/secrets/automation/glpi.json
install -d -m 0700 /opt/cosmotech/secrets/automation
if [[ ! -s "$credential_file" ]]; then
  container="$(docker ps -q --filter label=com.docker.compose.service=glpi)"
  kestra="$(docker ps -q --filter label=com.docker.compose.service=kestra)"
  [[ -n "$container" && -n "$kestra" ]] || exit 1
  gateway="$(docker inspect "$container" --format '{{(index .NetworkSettings.Networks "cosmotech-itsm-apps").Gateway}}')"
  kestra_ip="$(docker inspect "$kestra" --format '{{(index .NetworkSettings.Networks "cosmotech-itsm-apps").IPAddress}}')"
  docker cp "$script_dir/create-glpi-service.php" "$container":/tmp/cosmotech-create-service.php
  docker exec -e "COSMOTECH_ALLOWED_IPS=127.0.0.1,$gateway,$kestra_ip" \
    "$container" php /tmp/cosmotech-create-service.php
  # An already-existing service user intentionally causes PHP to stop instead
  # of creating a duplicate or rotating an unknown password. Recover its existing
  # protected credential file from SSM before retrying in that situation.
  docker cp "$container":/tmp/cosmotech-glpi-service.json "$credential_file"
  chmod 0600 "$credential_file"
  docker exec "$container" rm -f /tmp/cosmotech-glpi-service.json /tmp/cosmotech-create-service.php
fi
aws ssm put-parameter --name /cosmotech/itsm/glpi/automation-credentials \
  --type SecureString --overwrite --value "file://$credential_file" \
  --description 'Dedicated lab integration identity; no human approval rights' >/dev/null
echo 'Technical credentials synchronized with SSM SecureString; no personal identity changed.'
