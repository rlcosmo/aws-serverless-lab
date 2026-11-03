# Live infrastructure audit and implementation status

Audit date: 2026-11-03. This report reflects live AWS and Kubernetes observations made during the lab implementation. No SQS messages, DynamoDB item bodies, or Kubernetes Secret values were read. Existing application data was not intentionally modified or removed.

## AWS account and network

- Target account `414053644145`, region `us-east-1`; the AWS account plan was upgraded from `FREE` to `PAID` to permit the requested EC2 type. Existing promotional credits remained available immediately after the upgrade. The paid plan can incur charges beyond remaining credits.
- Existing EKS cluster `aws-eks-istio-lab-dev` is ACTIVE on Kubernetes 1.37. It has a managed Spot node group of `c7i-flex.large` instances, initially desired 2/max 3. A third node was requested to address insufficient schedulable memory; its provisioning and workload recovery remain to be verified.
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
- The active `orders-api` and `orders-worker` pods were Ready in the latest sample. Separate legacy deployments in namespace `orders` remain unhealthy: the API readiness probe returns 503; the worker exits because `SQS_QUEUE_URL` and `DYNAMODB_TABLE` are absent. They were not deleted or changed because their ownership and dependencies are not represented in repository code.
- `istiod` was Pending because the two existing nodes lacked schedulable memory. The EKS node group was asked to scale to its configured maximum of three; completion and scheduling remain to be confirmed.
- No PVCs were observed. Prometheus, Alertmanager, Loki, and Tempo persistence and recovery are not established.
- The Cluster Autoscaler logs contain forbidden reads for newer Kubernetes resource APIs. Their impact on scaling decisions has not yet been fully assessed.

## Terraform state and ITSM host

- A dedicated state bucket, `aws-serverless-lab-414053644145-tfstate-use1`, was created with S3 versioning, server-side encryption, public-access block, TLS-only bucket policy, and `prevent_destroy`. The DEV state was migrated using Terraform's state migration procedure. A local state backup remains ignored and must not be committed or deleted before an explicit recovery review.
- The Terraform DEV environment now provisions the private ITSM host, dedicated security group and instance role, SSM access, EKS read-only access, and daily AWS Backup with 14-day retention.
- EC2 `i-0def4e806c49cf60e` (`t3.large`) is running in a private subnet with no public IP, IMDSv2 required, and an encrypted 50 GiB gp3 root volume. The instance status was still initializing at last check and it had not registered in Systems Manager yet. Consequently GLPI and Kestra are **not yet verified installed or usable**.
- The host user-data installs Docker/Compose, AWS CLI, Terraform, kubectl, Helm, and SSM Agent, then bootstraps GLPI and Kestra. Verify cloud-init logs, SSM registration, container health, credential rotation, and application sign-in before considering the ITSM stack complete.
- GLPI and Kestra have separate databases and volumes. Ports bind to loopback for SSM forwarding; no public listener or ingress rule is configured. Generated credentials are written to SSM SecureString. The Kestra Docker task runner has Docker socket access and therefore host-level privileges; workflows must be limited to trusted operators.

## Repository and automation

- Terraform owns the serverless resources and new ITSM host. It does not own the existing EKS cluster, node group, live application deployments, Istio, or observability Helm releases.
- GitHub Actions validation was added for Python lint/tests, Lambda artifacts, Terraform formatting, and Terraform configuration validation. It does not deploy. There are no tracked Kubernetes manifests or a narrowly scoped GitHub OIDC deployment role yet.
- The nested `cosmotech-infrastructure-mcp` repository remains a separate project and must not be staged or committed through the parent repository.

## Priority backlog

| Priority | Item | Completion evidence |
| --- | --- | --- |
| P0 | Confirm EC2 bootstrap, SSM registration, GLPI/Kestra login, database health, and backup selection. | SSM-managed status Online, all Compose health checks healthy, both admin logins work, and a recovery procedure is exercised. |
| P0 | Stabilize EKS capacity and Istio. | Node group update completes, all nodes Ready, `istiod` Ready, no unschedulable required pods. |
| P0 | Resolve legacy `orders` deployments with their owner/configuration. | Restore readiness using an identified source of truth or document an approved retirement; preserve data and queues. |
| P1 | Track the live EKS, Istio, application, and observability state in versioned IaC/manifests. | Drift report reconciled and repeatable validation/deployment path. |
| P1 | Define observability persistence, retention, backups, and recovery. | PVC/storage design and verified restore; avoid relying on ephemeral pod storage. |
| P1 | Implement and test a notification destination. | Controlled alert reaches an approved receiver. |
| P1 | Implement durable order state and idempotent business processing. | API → SQS → worker → DynamoDB integration, retry/DLQ recovery tests, and trace propagation. |
| P1 | Add a DEV-only deployment workflow using GitHub OIDC. | Trust limited to this repository and protected main/environment; IAM permissions reviewed and post-deploy health checks pass. |
| P2 | Expand application, network, and IAM audit coverage. | Least-privilege review, backup restore evidence, endpoint and public exposure tests. |

## Validation recorded

Local project validation previously passed: 38 pytest tests, `compileall`, `pip check`, Ruff, Terraform formatting and validation, and Compose configuration syntax. The CI workflow has just been added and still requires a GitHub Actions run. Live Kubernetes status and ITSM bootstrap are asynchronous and are not declared complete until rechecked.
