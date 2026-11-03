# Implementation backlog

The cloud environment already contains live workloads and user data. Changes are made incrementally, with Terraform plans and health checks reviewed before applying. Deletion, replacement of data-bearing resources, and destructive recovery actions are out of scope.

## Completed in this implementation

- Restricted the API Gateway order route to AWS IAM authorization and verified anonymous calls receive 403.
- Restricted the existing observability ALB ingress to the existing administrator source range.
- Created a versioned, encrypted, TLS-only private S3 backend with native lock files and migrated DEV Terraform state.
- Added a reusable Terraform module for a private Ubuntu 24.04 `t3.large` host with encrypted gp3 storage, IMDSv2, dedicated IAM/SG, SSM access, EKS read-only access, and AWS Backup retention.
- Created the ITSM EC2 in the existing private subnet. Its user-data bootstrap is still being verified; GLPI/Kestra are not complete until their SSM and application health checks pass.
- Added pinned Docker Compose definitions for separate GLPI/MariaDB and Kestra/PostgreSQL services, local-only listeners, generated credentials, and operational runbook.
- Added GitHub Actions validation for Python lint/tests, Lambda artifacts, Terraform formatting, and Terraform configuration validation.

## Active priority work

1. Verify host cloud-init completion, SSM registration, Docker service health, GLPI and Kestra login, secrets retrieval path, and backup selection. Repair bootstrap errors without replacing the instance or volumes.
2. Verify the EKS node group scale-up and restore `istiod` scheduling. Preserve the existing namespace `orders` workloads while identifying their source of truth and missing configuration.
3. Create tracked Kubernetes/Helm configuration for workloads and observability, then reconcile it against live objects before changing them.
4. Configure durable observability storage, retention, and recovery. No PVCs were observed during the live audit.
5. Configure an actual notification receiver and test a controlled alert.
6. Implement durable Orders processing, DynamoDB state transitions, retries/idempotency, DLQ operations, and API → SQS → worker → DynamoDB integration tests.
7. Add a tightly scoped DEV-only GitHub OIDC deployment role and deployment gates only after the infrastructure and Kubernetes sources of truth exist.

## Validation and operations

- Run Ruff, pytest, compileall, dependency checks, Lambda artifact validation, Terraform format/validate, and Compose config validation locally and in CI.
- Review every Terraform plan for resource replacement, data impact, network exposure, IAM scope, and cost before apply. Never use Terraform destroy.
- Keep the parent project and `cosmotech-infrastructure-mcp` repository independent. Do not stage the nested MCP repository from the parent.
