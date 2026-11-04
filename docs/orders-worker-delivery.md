# Orders applications: worker extraction and DEV delivery

Worker source was missing from the canonical component repositories. It is now
published privately at https://github.com/rlcosmo/cosmotech-orders-worker with API
repository ancestry preserved and shared Orders modules retained as a snapshot.
The worker owns its Dockerfile, polling runtime, read-only HTTP health and CI/CD.
The independent MCP repository and unrelated local changes were left untouched.

CI evidence: https://github.com/rlcosmo/cosmotech-orders-worker/actions/runs/41922033711
passed lint, 63 tests, Docker build and Trivy HIGH/CRITICAL scanning. ECR publish
and GitOps proposal were skipped because worker delivery configuration is absent.
This evidence does not claim a deployment or reachable public endpoints.

Coordinated PRs:
- Infrastructure: https://github.com/rlcosmo/cosmotech-infrastructure-iac/pull/1
  adds worker-only OIDC/ECR publishing, two WAF hostname/rate rules and persistent
  Argo namespace registration. Terraform fmt/validate passed locally; refreshed
  plan/security review and deployment remain required. Existing IaC CI cannot apply.
- Kubernetes RBAC: https://github.com/rlcosmo/cosmotech-kubernetes-rbac/pull/1
  grants namespace-scoped worker delivery plus API/worker HPA/Ingress management,
  preserving workload visibility and get pods/log without granting Secrets.
- GitOps: https://github.com/rlcosmo/cosmotech-gitops/pull/3 adds worker Application,
  separate worker image-only promotion policy, HPA and HTTPS host for both apps,
  plus CI manifest and negative promotion validation. Six promotion tests passed.

Desired hosts are orders-api-dev.cosmotechsolutions.com.br and
orders-worker-dev.cosmotechsolutions.com.br. Worker exposes only /health/live and
/health/ready; API remains the SQS entrypoint. Both HPAs target container CPU 70%,
1–4 replicas, 300s scale-down stabilization. Argo must ignore spec.replicas. Existing
metrics-server/ContainerResource support and capacity must be verified at delivery.
CPU HPA does not measure SQS backlog. More replicas may increase node/API costs.

Activation requires a reviewed refreshed infrastructure plan, scoped role/WAF
installation through an authorized delivery process, worker ECR_PUBLISH_ROLE_ARN,
GitOps App ID/private-key secret, optional DEV_AUTO_PROMOTE=true, scoped RBAC,
existing Argo cluster namespace extension and management bootstrap delivery.
Publish/promote the new health-enabled image before enabling worker automated
sync; historical worker images lack the HTTP listener. Create the two Cloudflare
DNS CNAMEs pointing at the current shared ALB; verify wildcard TLS and WAF routes.
Do not merge API GitOps configuration before its bootstrap/RBAC prerequisites.

Existing queue age/DLQ/processing-error alerts remain operational requirements.
Queue visibility/retries, idempotency, data model and retention stay unchanged.
Recover by pausing promotion/sync and reverting the validated GitOps image/config;
never reset queue contents, tables or inventory. Detailed deployment order and
rollback are in the infrastructure PR docs/orders-worker-delivery.md.
