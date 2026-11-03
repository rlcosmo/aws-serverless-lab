#!/usr/bin/env bash
set -Eeuo pipefail

CLUSTER_NAME="${EKS_CLUSTER_NAME:-aws-eks-istio-lab-dev}"
NAMESPACE="${OBSERVABILITY_INGRESS_NAMESPACE:-istio-system}"
INGRESS_NAME="${OBSERVABILITY_INGRESS_NAME:-grafana-public}"

CIDR="$(aws eks describe-cluster \
  --name "$CLUSTER_NAME" \
  --query 'cluster.resourcesVpcConfig.publicAccessCidrs' \
  --output json | python3 -c 'import ipaddress,json,sys; values=json.load(sys.stdin); assert len(values)==1; net=ipaddress.ip_network(values[0],strict=False); assert net.version==4 and net.prefixlen==32 and not net.is_private and not net.is_unspecified; print(net)')"

kubectl annotate ingress "$INGRESS_NAME" \
  -n "$NAMESPACE" \
  "alb.ingress.kubernetes.io/inbound-cidrs=$CIDR" \
  --overwrite >/dev/null

ACTUAL="$(kubectl get ingress "$INGRESS_NAME" -n "$NAMESPACE" -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)["metadata"]["annotations"]["alb.ingress.kubernetes.io/inbound-cidrs"])')"
if [ "$ACTUAL" != "$CIDR" ]; then
  printf '%s\n' 'Ingress source-range verification failed.' >&2
  exit 1
fi

printf '%s\n' 'Observability ingress is restricted to the EKS administrator /32.'
