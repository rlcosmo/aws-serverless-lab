# Remaining implementation work

Current evidence and historical execution are in [EXECUTION-STATUS.md](EXECUTION-STATUS.md). Existing healthy installations must be preserved.

## Completed foundation

Encrypted observability PVC migration/restart, AWS Backup selection and isolated EBS/database recovery, GLPI technical OAuth and functional test records, confirmed SNS destination and provider delivery, externally hosted TLS/WAF/authentication checks, removal of only the two authorized legacy Deployments, scoped repository OIDC and four protected reviewer environments are implemented. New Orders processing and automation candidates are versioned and unit-tested; live deployment remains gated.

## Dependencies and remaining tests

1. Resolve officially supported independent Kestra technical authentication. Owner has no Enterprise license; preserve personal Basic Auth and do not disable authentication. Candidate flow is disabled, not engine-tested. Workflow execution, logs, restart persistence and GLPI integration still need authenticated technical tests.
2. Owner registers/installs a repository-limited GitHub App and securely stores its credential. Complete the GLPI/Kestra/Actions/GLPI integration test before enabling `GMUD_INTEGRATION_READY`.
3. Owner approves each real DEV, QA, PO/PM and Infra/SRE gate. Approval probe verifies no deploy can start while waiting. OIDC/private EKS tunnel runtime validation must complete after those real approvals. Then review and deploy the Orders candidate and record actual live business/trace evidence.
4. Match Cluster Autoscaler minor to Kubernetes 1.37 when the upstream 1.37 binary exists. Current 1.36.1 authorization checks pass; the minor mismatch remains unresolved.
5. Schedule protected logical MariaDB/PostgreSQL dumps and application-consistent Tempo captures; ordinary daily EBS snapshots are crash-consistent. Keep failed/working restore copies until evidence retention is accepted, then review their cost and explicit cleanup authorization.
6. Perform a separate whole-EC2 restore/boot exercise if full-host recovery evidence is required; current proof covers EBS and isolated logical DB integrity. Review EKS Orders PITR/retention as a separate change.
7. Owner confirms inbox receipt of both alert and recovery; SNS provider delivery has succeeded. No personal mailbox access is available to automation.

The preserved invalid DLQ message must not be replayed unchanged. Its schema failure, hash and duplication precautions are in [orders processing](orders-processing.md).

## Change discipline

Review Terraform plans, IAM scope, resource replacement, retained data and cost before changes. Run affected tests and CI. Keep the independent untracked `cosmotech-infrastructure-mcp/` out of parent commits. Never simulate human approvals or rotate existing personal credentials to unblock tests.
