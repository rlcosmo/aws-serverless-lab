#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_CONFIG=/opt/cosmotech/itsm/application.yaml

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y nginx

install -o root -g root -m 0644 "$SCRIPT_DIR/nginx/itsm-public.conf" /etc/nginx/conf.d/cosmotech-itsm-public.conf
if [ -L /etc/nginx/sites-enabled/default ]; then
  rm /etc/nginx/sites-enabled/default
fi

if [ -s "$APP_CONFIG" ]; then
  python3 - "$APP_CONFIG" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
contents = path.read_text()
old = "url: http://localhost:8081/"
new = "url: https://kestra.cosmotechsolutions.com.br/"
if new not in contents:
    if old not in contents:
        raise SystemExit("Kestra public URL was not updated: expected URL setting was not found")
    path.write_text(contents.replace(old, new, 1))
PY
  chown root:docker "$APP_CONFIG"
  chmod 0440 "$APP_CONFIG"
  if docker compose --project-name cosmotech-itsm --env-file /opt/cosmotech/secrets/itsm/runtime.env --file "$SCRIPT_DIR/docker-compose.yml" ps --services --filter status=running | grep -qx kestra; then
    docker compose --project-name cosmotech-itsm --env-file /opt/cosmotech/secrets/itsm/runtime.env --file "$SCRIPT_DIR/docker-compose.yml" up -d --no-deps kestra
  fi
fi

nginx -t
systemctl enable --now nginx
systemctl reload nginx
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:8088/healthz >/dev/null
printf '%s\n' 'Private Nginx reverse proxy is ready on TCP/8088; credentials and query strings are excluded from access logs.'
