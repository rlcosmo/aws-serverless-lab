#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
secret_dir=/opt/cosmotech/secrets/automation/kestra-oss
data_dir=/opt/cosmotech/itsm-automation
install -d -m 0700 "$secret_dir" "$data_dir"
if [[ ! -s "$secret_dir/runtime.env" ]]; then
  [[ ! -s "$secret_dir/credentials.json" ]] || { echo 'Incomplete existing credentials; refusing rotation'; exit 1; }
  [[ "$(awk '/MemAvailable:/{print $2}' /proc/meminfo)" -ge 2000000 ]] || { echo 'Insufficient available memory'; exit 1; }
  if docker volume inspect cosmotech-automation-postgres >/dev/null 2>&1; then
    echo 'Existing database without matching credentials; refusing replacement'; exit 1
  fi
  python3 - "$secret_dir" <<'PY'
import json,pathlib,secrets,sys
root=pathlib.Path(sys.argv[1]);password='Aa1'+secrets.token_hex(32)
values={'AUTOMATION_USERNAME':'svc-cosmotech-automation@cosmotechsolutions.com.br',
        'AUTOMATION_PASSWORD':password,'AUTOMATION_DB_PASSWORD':secrets.token_hex(32),
        'AUTOMATION_ENCRYPTION_KEY':secrets.token_hex(32)}
(root/'runtime.env').write_text(''.join(f'{k}={v}\n' for k,v in values.items()))
(root/'credentials.json').write_text(json.dumps({'username':values['AUTOMATION_USERNAME'],
    'password':password,'base_url':'http://127.0.0.1:8082'}))
for p in root.iterdir():p.chmod(0o600)
PY
fi
install -d -m 0750 -o 1000 -g 1000 "$data_dir/tmp"
install -m 0644 "$source_dir/application.yaml" "$data_dir/application.yaml"
install -m 0644 "$source_dir/docker-compose.yml" "$data_dir/docker-compose.yml"
export DOCKER_GID="$(stat -c '%g' /var/run/docker.sock)"
compose=(docker compose --project-name cosmotech-automation --env-file "$secret_dir/runtime.env" --file "$data_dir/docker-compose.yml")
"${compose[@]}" config --quiet
"${compose[@]}" up -d
aws ssm put-parameter --name /cosmotech/itsm/kestra-automation/credentials --type SecureString \
  --overwrite --value "file://$secret_dir/credentials.json" >/dev/null
printf 'Dedicated private automation engine started; personal services unchanged.\n'
"${compose[@]}" ps --format '{{.Name}} {{.State}} {{.Health}}'

docker build --quiet -f "$source_dir/Dockerfile.runner" -t cosmotech-automation-runner:lab-20261104 "$source_dir" > /opt/cosmotech/itsm-automation/runner-build.log 2>&1
python3 "$source_dir/validate_kestra_automation.py"
