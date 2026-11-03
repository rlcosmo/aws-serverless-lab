# Live infrastructure audit and implementation status

Audit date: 2026-11-03. This report reflects live AWS and Kubernetes observations made during the lab implementation. No SQS messages, DynamoDB item bodies, or Kubernetes Secret values were read. Existing application data was not intentionally modified or removed.

## AWS account and network

- Target account `414053644145`, region `us-east-1`; the AWS account plan was upgraded from `FREE` to `PAID` to permit the requested EC2 type. Existing promotional credits remained available immediately after the upgrade. The paid plan can incur charges beyond remaining credits.
- Existing EKS cluster `aws-eks-istio-lab-dev` is ACTIVE on Kubernetes 1.37. It has a managed Spot node group of `c7i-flex.large` instances, now desired 3/max 3. The update completed successfully; all three nodes are Ready and `istiod` is `1/1 Running`.
- Existing VPC has private subnets and NAT egress. The new ITSM host uses an existing private subnet and has no public IP.
- The AWS Load Balancer Controller manages an internet-facing ALB for observability ingress. TLS hostnames were valid during the prior audit; ingress source ranges were restricted to the existing administrator `/32`. Grafana required authentication; unauthenticated Prometheus, Alertmanager, and Tempo access was previously observed from the administrator source range. Repeat checks after changes.

## Serverless and data

- Terraform manages the HTTP API, two Lambda functions, SQS source and DLQ queues, DynamoDB, CloudWatch logs, alarms, and dashboard.
- `POST /orders` requires AWS IAM SigV4; an unsigned request returned 403 during the prior audit.
- The Lambda scaffold publishes an event and provides idempotency claims, but the consumer business operation is still a no-op seam. The full deployed EKS Orders service is separate and does not make the Lambda scaffold an end-to-end durable workflow.
- A preexisting DLQ had one message at initial audit. The message was not inspected, replayed, or deleted. Existing DynamoDB tables contain user data and were not read.
- Terraform alarms have no verified notification destination. There is no evidence yet of a functioning end-to-end alert delivery path.

## EKS and observability

- Helm releases observed: AWS Load Balancer Controller, Kyverno, Alloy, Loki, OpenTelemetry Collector, Prometheus stack, and Tempo. No Kubernetes manifests or Helm values for the live stack are tracked in this repository.
- The active `orders-api` and `orders-worker` pods are Ready. The legacy worker in namespace `orders` still crashes because its `orders-config` ConfigMap has empty `SQS_QUEUE_URL` and `DYNAMODB_TABLE` values; its API readiness probe returns 503. These deployments remain untouched because their ownership and source of truth are not represented in repository code.
- No PVCs were observed. Prometheus, Alertmanager, Loki, and Tempo persistence and recovery are not established.
- The Cluster Autoscaler logs contain forbidden reads for newer Kubernetes resource APIs. Their impact on scaling decisions has not yet been fully assessed.

## Terraform state and ITSM host

- A dedicated state bucket, `aws-serverless-lab-414053644145-tfstate-use1`, was created with S3 versioning, server-side encryption, public-access block, TLS-only bucket policy, and `prevent_destroy`. The DEV state was migrated using Terraform's state migration procedure. A local state backup remains ignored and must not be committed or deleted before an explicit recovery review.
- The Terraform DEV environment now provisions the private ITSM host, dedicated security group and instance role, SSM access, EKS read-only access, and daily AWS Backup with 14-day retention.
- EC2 `i-0def4e806c49cf60e` (`t3.large`) is running in a private subnet with no public IP, IMDSv2 required, an encrypted 50 GiB gp3 root volume, passing system checks, and SSM status Online.
- The first user-data run failed because the host SG had no active egress, Ubuntu apt sources used HTTP while egress permitted HTTPS only, and Ubuntu 24.04 had no `awscli` apt candidate. These issues are corrected in source: Terraform manages HTTPS/DNS egress, bootstrap converts apt sources to HTTPS, AWS CLI v2 comes from the signed Snap Store, and the repository is cloned before tool installation.
- GLPI, MariaDB, Kestra, and PostgreSQL run from pinned images. GLPI and both databases report healthy, and GLPI returns HTTP 200. Kestra initially failed because its non-root process could not write the new named volume. A network-isolated, capability-limited init container now assigns UID 1000 ownership; after the live correction, Kestra remained running with no restarts, its root returned HTTP 307, and its unauthenticated API returned HTTP 401. Authenticated API verification remains pending.
- Bootstrap completion markers are present, and both generated administrator passwords were stored in SSM SecureString parameters. Verify authenticated API access and both UI logins before considering ITSM fully operational.
- GLPI and Kestra have separate databases and volumes. Ports bind to loopback for SSM forwarding; no public listener or ingress rule is configured. Generated credentials are written to SSM SecureString. The Kestra Docker task runner has Docker socket access and therefore host-level privileges; workflows must be limited to trusted operators.

## Repository and automation

- Terraform owns the serverless resources and new ITSM host. It does not own the existing EKS cluster, node group, live application deployments, Istio, or observability Helm releases.
- GitHub Actions validation for Python lint/tests, Lambda artifacts, Terraform formatting, and Terraform configuration validation passed on [run 41734798857](https://github.com/rlcosmo/aws-serverless-lab/actions/runs/41734798857). It does not deploy. There are no tracked Kubernetes manifests or a narrowly scoped GitHub OIDC deployment role yet.
- The nested `cosmotech-infrastructure-mcp` repository remains a separate project and must not be staged or committed through the parent repository.

## Priority backlog

| Priority | Item | Completion evidence |
| --- | --- | --- |
| P0 | Verify ITSM authentication and practice recovery. | Authenticated Kestra API request and both UI logins succeed; AWS Backup recovery path is exercised. |
| P0 | Resolve legacy `orders` deployments with their owner/configuration. | Restore readiness using an identified source of truth or document an approved retirement; preserve data and queues. |
| P1 | Keep EKS capacity stable and investigate autoscaler RBAC warnings. | All nodes and required pods remain Ready; autoscaler handles pending workloads without repeated forbidden API warnings. |
| P1 | Track the live EKS, Istio, application, and observability state in versioned IaC/manifests. | Drift report reconciled and repeatable validation/deployment path. |
| P1 | Define observability persistence, retention, backups, and recovery. | PVC/storage design and verified restore; avoid relying on ephemeral pod storage. |
| P1 | Implement and test a notification destination. | Controlled alert reaches an approved receiver. |
| P1 | Implement durable order state and idempotent business processing. | API → SQS → worker → DynamoDB integration, retry/DLQ recovery tests, and trace propagation. |
| P1 | Add a DEV-only deployment workflow using GitHub OIDC. | Trust limited to this repository and protected main/environment; IAM permissions reviewed and post-deploy health checks pass. |
| P2 | Expand application, network, and IAM audit coverage. | Least-privilege review, backup restore evidence, endpoint and public exposure tests. |

## Validation recorded

Local project validation passed: 38 pytest tests, `compileall`, `pip check`, Ruff, Terraform formatting and validation, and Compose configuration syntax. The GitHub Actions validation workflow passed. Live EKS capacity and ITSM services are running; UI authentication and backup recovery remain to be proven.
