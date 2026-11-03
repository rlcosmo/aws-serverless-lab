# Implementation backlog

The cloud environment already contains live workloads and user data. Changes are made incrementally, with Terraform plans and health checks reviewed before applying. Deletion, replacement of data-bearing resources, and destructive recovery actions are out of scope.

## Completed in this implementation

- Restricted the API Gateway order route to AWS IAM authorization and verified anonymous calls receive 403.
- Restricted the existing observability ALB ingress to the existing administrator source range.
- Created a versioned, encrypted, TLS-only private S3 backend with native lock files and migrated DEV Terraform state.
- Added a reusable Terraform module for a private Ubuntu 24.04 `t3.large` host with encrypted gp3 storage, IMDSv2, dedicated IAM/SG, SSM access, EKS read-only access, and AWS Backup retention.
- Created the ITSM EC2 in the existing private subnet; SSM and Docker Compose health checks pass after a host restart.
- Deployed pinned Docker Compose definitions for separate GLPI/MariaDB and Kestra/PostgreSQL services, local-only listeners, generated credentials, and operational runbook. Authenticated Kestra API succeeds. GLPI's UI login and AWS Backup restore remain unverified.
- Added GitHub Actions validation for Python lint/tests, Lambda artifacts, Terraform formatting, and Terraform configuration validation; the latest run passed.
- Implemented version 2 full-order queue events, conditional DynamoDB order persistence, versioned idempotency claims, scoped consumer IAM, SQS 1 MiB message limits, and DynamoDB point-in-time recovery. A signed live smoke test posted one synthetic order twice and confirmed a single `RECEIVED` record.
- Verified Prometheus, Grafana, Loki, Tempo, and OTel pods are ready. Restricted the existing observability ALB ingress to the administrator `/32`; dashboards remain admin-only. Current Helm values and Kubernetes manifests are not yet tracked, no PVCs exist, and alerts have no verified receiver.

## Active priority work

1. Verify GLPI UI login and exercise AWS Backup recovery using a separate restored host/volume; retain the original instance and backups until recovery is proven.
2. Reconcile the two non-ready duplicate deployments in namespace `orders` after identifying ownership and intended queue/table. Their missing ConfigMap values make them risky to activate alongside the healthy `orders-api` and `orders-worker` deployments.
3. Create tracked Kubernetes/Helm configuration for workloads and observability, then reconcile it against live objects before changing them. Review Cluster Autoscaler's repeated forbidden reads of storage/resource API groups and match its version to the cluster before changing RBAC or upgrading it.
4. Configure durable observability storage, retention, and recovery. No PVCs or EBS CSI driver were observed; the only StorageClass is legacy `gp2` with a `Delete` reclaim policy.
5. Configure an approved, functional notification receiver and test a controlled alert. The receiver identity/endpoint is not present in the repository or AWS environment.
6. Extend durable order intake into inventory/payment/fulfillment semantics, trace propagation, retry and DLQ recovery tests. The current serverless path only records `RECEIVED` orders; EKS and serverless deployments remain separate.
7. Add a tightly scoped DEV-only GitHub OIDC deployment workflow only after application/container sources and Kubernetes source-of-truth are tracked. Current CI is validation-only. The existing ECR publish role trusts only the separate `rlcosmo/aws-eks-istio-lab` repository and cannot be reused by this repository as-is.

## Validation and operations

- Run Ruff, pytest, compileall, dependency checks, Lambda artifact validation, Terraform format/validate, and Compose config validation locally and in CI.
- Review every Terraform plan for resource replacement, data impact, network exposure, IAM scope, and cost before apply. Never use Terraform destroy.
- Keep the parent project and `cosmotech-infrastructure-mcp` repository independent. Do not stage the nested MCP repository from the parent.
