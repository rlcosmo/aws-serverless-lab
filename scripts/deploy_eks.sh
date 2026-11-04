#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

mode="${DEPLOY_MODE:?DEPLOY_MODE is required}"
[[ "$mode" == approval-probe || "$mode" == deploy ]] || exit 2
[[ "${GITHUB_SHA:?}" =~ ^[a-f0-9]{40}$ ]] || exit 2
[[ "${GITHUB_REF:?}" == refs/heads/main ]] || exit 2

region=us-east-1
account=414053644145
cluster=aws-eks-istio-lab-dev
registry="$account.dkr.ecr.$region.amazonaws.com"
work_dir="$(mktemp -d "${RUNNER_TEMP:-/tmp}/cosmotech-deploy.XXXXXX")"
export KUBECONFIG="$work_dir/kubeconfig"
tunnel_pid=''
cleanup() {
  if [[ -n "$tunnel_pid" ]]; then kill "$tunnel_pid" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

aws sts get-caller-identity --query Arn --output text
aws ssm start-session --region "$region" --target i-0def4e806c49cf60e \
  --document-name CosmoTech-GitHub-EKS-Tunnel > "$work_dir/tunnel.log" 2>&1 &
tunnel_pid=$!
python - <<'PY'
import socket,time
for attempt in range(45):
    try:
        with socket.create_connection(('127.0.0.1',8443),timeout=1):break
    except OSError:time.sleep(1)
else:raise SystemExit('Private EKS tunnel did not become available')
PY
aws eks update-kubeconfig --region "$region" --name "$cluster" --kubeconfig "$KUBECONFIG"
endpoint="$(aws eks describe-cluster --region "$region" --name "$cluster" --query cluster.endpoint --output text)"
context="arn:aws:eks:$region:$account:cluster/$cluster"
kubectl config set-cluster "$context" --server=https://127.0.0.1:8443 --tls-server-name="${endpoint#https://}"
kubectl auth can-i patch deployment/orders-api -n orders-api
kubectl auth can-i patch deployment/orders-worker -n orders-worker
if kubectl auth can-i get secrets -n orders-api; then
  echo 'Unexpected Secret read access; deployment blocked.' >&2
  exit 1
fi
if [[ "$mode" == approval-probe ]]; then
  echo 'Real approvals, OIDC and private EKS access verified. No application deployment requested.'
  exit 0
fi

# An empty inventory catalog is a configuration error, not zero stock.
aws dynamodb get-item --region "$region" --table-name aws-eks-istio-lab-dev-orders-data \
  --key '{"order_id":{"S":"INVENTORY#LAB"}}' --projection-expression order_id \
  --consistent-read > "$work_dir/inventory-check.json"
python - "$work_dir/inventory-check.json" <<'PY'
import json,sys
if not json.load(open(sys.argv[1])).get('Item'):raise SystemExit('Lab inventory is not configured')
PY

aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$registry"
for component in api worker; do
  repository="aws-eks-istio-lab-dev-orders-$component"
  tag="lab-$GITHUB_SHA"
  if ! aws ecr describe-images --region "$region" --repository-name "$repository" \
    --image-ids "imageTag=$tag" > "$work_dir/$component-image.json" 2>/dev/null; then
    docker build -f "src/orders/runtime/Dockerfile.$component" \
      --label "org.opencontainers.image.revision=$GITHUB_SHA" \
      --label org.opencontainers.image.source=https://github.com/rlcosmo/aws-serverless-lab \
      -t "$registry/$repository:$tag" .
    docker push "$registry/$repository:$tag"
    aws ecr describe-images --region "$region" --repository-name "$repository" \
      --image-ids "imageTag=$tag" > "$work_dir/$component-image.json"
  fi
done

# Resolve both immutable digests before changing either workload.
python - "$work_dir" "$registry" "$GITHUB_SHA" <<'PY'
import json,sys,pathlib
root=pathlib.Path(sys.argv[1]);evidence={'commit_sha':sys.argv[3],'images':{}}
for component in ['api','worker']:
    digest=json.load(open(root/f'{component}-image.json'))['imageDetails'][0]['imageDigest']
    image=f'{sys.argv[2]}/aws-eks-istio-lab-dev-orders-{component}@{digest}'
    evidence['images'][component]=image
    patch={'spec':{'template':{'spec':{'containers':[{'name':f'orders-{component}','image':image,
        'env':[{'name':'ORDERS_KEY_SCHEMA','value':'legacy'},
               {'name':'OTEL_EXPORTER_OTLP_ENDPOINT','value':'http://otel-collector-opentelemetry-collector.observability.svc.cluster.local:4318'}]}]}}}}
    (root/f'{component}-patch.json').write_text(json.dumps(patch))
pathlib.Path('deploy-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
PY
for component in api worker; do
  kubectl get deployment "orders-$component" -n "orders-$component" \
    -o json > "$work_dir/$component-before.json"
  python - "$work_dir/$component-before.json" "$component" <<'PY'
import json,sys,pathlib
evidence_path=pathlib.Path('deploy-evidence.json');evidence=json.loads(evidence_path.read_text())
spec=json.load(open(sys.argv[1]))['spec']['template']['spec']
evidence.setdefault('previous_images',{})[sys.argv[2]]={c['name']:c['image'] for c in spec['containers']}
evidence_path.write_text(json.dumps(evidence,indent=2)+'\n')
PY
  kubectl patch deployment "orders-$component" -n "orders-$component" \
    --type=strategic --patch-file "$work_dir/$component-patch.json"
  kubectl rollout status deployment/"orders-$component" -n "orders-$component" --timeout=180s
done
python - "$work_dir/canary-order.json" <<'PY'
import json,os,sys
json.dump({'order_id':'cosmotech-gmud-'+os.environ['GITHUB_RUN_ID'],
           'items':[{'sku':'LAB-SKU-001','quantity':1}]},open(sys.argv[1],'w'))
PY
kubectl create --raw /api/v1/namespaces/orders-api/services/orders-api:80/proxy/orders \
  -f "$work_dir/canary-order.json" > "$work_dir/canary-accepted.json"
python - "$work_dir" <<'PY'
import json,os,pathlib,subprocess,sys,time
root=pathlib.Path(sys.argv[1]);order_id='cosmotech-gmud-'+os.environ['GITHUB_RUN_ID']
for attempt in range(30):
    response=subprocess.run(['kubectl','get','--raw',
        '/api/v1/namespaces/orders-api/services/orders-api:80/proxy/orders/'+order_id],
        capture_output=True,text=True)
    if response.returncode==0:
        record=json.loads(response.stdout)
        if record.get('status')=='REJECTED':raise SystemExit('Controlled canary order was rejected')
        if record.get('status')=='COMPLETED':
            p=pathlib.Path('deploy-evidence.json');evidence=json.loads(p.read_text())
            evidence['canary']={'order_id':order_id,'status':'COMPLETED','synthetic':True}
            p.write_text(json.dumps(evidence,indent=2)+'\n');break
    time.sleep(2)
else:raise SystemExit('Controlled canary did not complete within 60 seconds')
PY
echo 'DEV rollout and synthetic API/SQS/worker processing passed; evidence is ready for GLPI.'
