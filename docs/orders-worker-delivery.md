# Automatic DEV application delivery

The owner confirmed automatic delivery without human approvals for API and worker;
approval stages will be added later. Worker extraction and the coordinated
infrastructure/RBAC/GitOps changes are merged and deployed. No pending approval
or manual image-patching step is part of the application delivery path.

Repositories: [Orders API](https://github.com/rlcosmo/cosmotech-orders-api),
[Orders Worker](https://github.com/rlcosmo/cosmotech-orders-worker),
[GitOps](https://github.com/rlcosmo/cosmotech-gitops).

Successful end-to-end evidence:
- [Worker CI 41924664660](https://github.com/rlcosmo/cosmotech-orders-worker/actions/runs/41924664660): lint, 63 tests, Docker build, Trivy, OIDC/ECR publication and automatic image-only promotion. Source cc8aa12e4fb72357143d26cdb9257fd10f2f3972; digest sha256:a5039455112304917d8fc0b25af414e34c823882a1f8712da74fbb412517a0f3.
- [API CI 41924915236](https://github.com/rlcosmo/cosmotech-orders-api/actions/runs/41924915236): test/build/scan, publication and automatic promotion from source 711e50193ac996ab93f1992b0316b2550940a89a.
- [GitOps delivery 41925158406](https://github.com/rlcosmo/cosmotech-gitops/actions/runs/41925158406): successful Argo reconciliation and external HTTPS health at exact main revision bfde9b7a8d70dd2d5dad45e0c94db7421f85252c. Earlier worker activation delivery 41924949369 also passed.
- GitOps image PRs #4 (worker) and #5 (API) were automatically merged by the existing GitHub App. No human approval was requested or simulated.

| Application | HTTPS host | HPA |
| --- | --- | --- |
| orders-api-dev | orders-api-dev.cosmotechsolutions.com.br | 1–4, container CPU 70% |
| orders-worker-dev | orders-worker-dev.cosmotechsolutions.com.br | 1–4, container CPU 70% |

Both applications expose /health/live and /health/ready. Worker accepts health
GETs only; business requests go to the API and arrive at the worker through SQS.
Each HPA has 300s downscale stabilization and one-pod/minute bounds. Argo ignores
spec.replicas so it does not undo autoscaling. DNS already resolved to the shared
ALB; no DNS change was required. Existing wildcard TLS and all prior WAF rules
are preserved; two new WAF host/rate rules cover these hosts.

Flow: app main push → tests/build/scan → immutable ECR image via dedicated OIDC
role → GitHub App validates SHA/digest and exact image-only GitOps diff → automatic
merge → GitOps main deliver-dev → fixed SSM document on the existing Argo host →
versioned AppProject/Application reconciliation → Argo EKS rollout → exact revision
Synced/Healthy check → public HTTPS health checks. Source and pipeline changes
trigger application CI. No GitHub Environment reviewer gate is configured in this
path. A missing worker publishing configuration now fails rather than silently skips.

The existing App secret was transferred using encryption addressed to the worker
repository public key. No plaintext secret was retrieved or logged. Roles trust
immutable repository/owner IDs and main only. The GitOps CI role can invoke only
the fixed synchronization document on the dedicated host and read status. Argo
RBAC is scoped to the two namespaces and does not permit Secret access. The
registration namespace list was extended without regenerating its credentials.

Infrastructure was installed from the canonical IaC repository after format,
validation, refreshed targeted plan review and IAM Access Analyzer checks. Plans
excluded unrelated Lambda/infrastructure changes. A successful SSM document
creation initially failed its Terraform readback because the temporary bootstrap
role lacked DescribeDocumentPermission; that permission was scoped, live content
was compared to reviewed source, taint was cleared without recreation, and a
fresh one-policy plan completed the integration. Initial delivery was retried
after role setup. The temporary bootstrap role/access bindings are removed after
verification. General IaC CI remains validate/plan; application delivery is fully
automatic through GitOps.

Existing idempotency, queue visibility/retries/DLQ, data model and retention are
preserved. Health smoke checks submit no valid order. Monitor queue age, DLQ,
processing errors, HPA ScalingActive and pod availability. CPU HPA is not SQS
backlog scaling. Extra replicas may increase node/AWS API costs; no extra ALB or
fixed application compute was created. Two WAF rules add rule charges.

Rollback: pause automatic sync/promotion, revert a validated image/config in
GitOps, then restore normal sync after review. Keep queues, tables and inventory
intact. The independent MCP repository and unrelated local changes are preserved.
