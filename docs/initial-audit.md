# Live infrastructure audit and implementation status

Audit date: 2026-11-03. This report reflects live AWS and Kubernetes observations made during the lab implementation. No SQS payloads, preexisting DynamoDB item bodies, or Kubernetes Secret values were read. The only item body inspected was the new synthetic canary order written for the smoke test. Existing application data was not intentionally modified or removed.

## AWS account and network

- Target account `414053644145`, region `us-east-1`; the AWS account plan was upgraded from `FREE` to `PAID` to permit the requested EC2 type. Existing promotional credits remained available immediately after the upgrade. The paid plan can incur charges beyond remaining credits.
- Existing EKS cluster `aws-eks-istio-lab-dev` is ACTIVE on Kubernetes 1.37. It has a managed Spot node group of `c7i-flex.large` instances, now desired 3/max 3. The update completed successfully; all three nodes are Ready and `istiod` is `1/1 Running`.
- Cluster API private and public access are enabled; the public endpoint CIDR is restricted to the administrator `/32`. Both ECR application repositories use immutable tags and scan-on-push.
- Both SQS source queues use server-side encryption, a five-receive redrive policy, and four-day retention; both DLQs retain messages for 14 days. The EKS queue and DLQ are empty. The serverless source queue is empty; its DLQ still has one preexisting visible message which was not read, replayed, or removed.
- Existing VPC has private subnets and NAT egress. The new ITSM host uses an existing private subnet and has no public IP.
- The AWS Load Balancer Controller manages an internet-facing ALB for observability ingress. TLS hostnames were valid during the prior audit; ingress source ranges were restricted to the existing administrator `/32`. Grafana required authentication; unauthenticated Prometheus, Alertmanager, and Tempo access was previously observed from the administrator source range. Repeat checks after changes.

## Serverless and data

- Terraform manages the HTTP API, two Lambda functions, SQS source and DLQ queues, DynamoDB, CloudWatch logs, alarms, and dashboard. The serverless DynamoDB table has point-in-time recovery enabled and retains TTL for idempotency claims; EKS application data is in a separate table with TTL and point-in-time recovery disabled.
- `POST /orders` requires AWS IAM SigV4; an unsigned request returned 403 during the prior audit.
- The Lambda path publishes version 2 events with complete validated order content, then conditionally persists `ORDER#<id>/ORDER` with status `RECEIVED`; idempotency keys are versioned and order data uses conditional writes. A signed API smoke test submitted the same synthetic order twice, returned 202 both times, and produced one persisted record and one completed idempotency claim. This is durable order intake, not inventory/payment/fulfillment. DynamoDB point-in-time recovery is enabled.
- A preexisting DLQ had one message at initial audit. The message was not inspected, replayed, or deleted. Existing DynamoDB tables contain user data and were not read.
- Terraform alarms have no verified notification destination. There is no evidence yet of a functioning end-to-end alert delivery path.

## EKS and observability

- Helm releases observed and deployed: AWS Load Balancer Controller, Kyverno, Alloy, Loki, OpenTelemetry Collector, Prometheus stack, and Tempo. All of their current pods report Ready. No Kubernetes manifests or Helm values for the live stack are tracked in this repository.
- The active `orders-api` and `orders-worker` deployments in their dedicated namespaces are Ready. The older duplicate deployments in namespace `orders` are not: API is `0/1` and worker is `0/1` with Error/restarts. Their ConfigMap has empty `SQS_QUEUE_URL` and `DYNAMODB_TABLE` values. These workloads remain untouched because ownership/source-of-truth is absent; changing them could start a second consumer against existing queues.
- The MCP aggregate health reports three Ready nodes and 40 pods in Running phase; readiness inspection shows the two legacy `orders` pods are not ready. There are no PVCs, so observability persistence and recovery are not established.
- No PVCs were observed. Prometheus, Alertmanager, Loki, and Tempo persistence and recovery are not established.
- The Cluster Autoscaler logs contain forbidden reads for newer Kubernetes resource APIs. Their impact on scaling decisions has not yet been fully assessed.

## Terraform state and ITSM host

- A dedicated state bucket, `aws-serverless-lab-414053644145-tfstate-use1`, was created with S3 versioning, server-side encryption, public-access block, TLS-only bucket policy, and `prevent_destroy`. The DEV state was migrated using Terraform's state migration procedure. A local state backup remains ignored and must not be committed or deleted before an explicit recovery review.
- The Terraform DEV environment now provisions the private ITSM host, dedicated security group and instance role, SSM access, EKS read-only access, and daily AWS Backup with 14-day retention.
- EC2 `i-0def4e806c49cf60e` (`t3.large`) is running in a private subnet with no public IP, IMDSv2 required, an encrypted 50 GiB gp3 root volume, passing system checks, and SSM status Online.
- The first user-data run failed because the host SG had no active egress, Ubuntu apt sources used HTTP while egress permitted HTTPS only, and Ubuntu 24.04 had no `awscli` apt candidate. These issues are corrected in source: Terraform manages HTTPS/DNS egress, bootstrap converts apt sources to HTTPS, AWS CLI v2 comes from the signed Snap Store, and the repository is cloned before tool installation.
- GLPI, MariaDB, Kestra, and PostgreSQL run from pinned images. All four report running, and GLPI/MariaDB/PostgreSQL health checks are healthy. GLPI home responds HTTP 200 and login path redirects with HTTP 302. A network-isolated, capability-limited init container assigns UID 1000 ownership to Kestra's storage. Authenticated Kestra API query returned HTTP 200; unauthenticated access returned HTTP 401. GLPI interactive administrator login has not been independently verified.
- Bootstrap completion markers are present, and generated administrator passwords are stored in SSM SecureString parameters. AWS Backup recovery has not been exercised.
- GLPI and Kestra have separate databases and volumes. Ports bind to loopback for SSM forwarding; no public listener or ingress rule is configured. Generated credentials are written to SSM SecureString. The Kestra Docker task runner has Docker socket access and therefore host-level privileges; workflows must be limited to trusted operators.

## Repository and automation

- Terraform owns the serverless resources and new ITSM host. It does not own the existing EKS cluster, node group, live application deployments, Istio, or observability Helm releases.
- GitHub Actions validation for Python lint/tests, Lambda artifacts, Terraform formatting, and Terraform configuration validation passed on [run 41739881815](https://github.com/rlcosmo/aws-serverless-lab/actions/runs/41739881815). It does not deploy. The account has an ECR-publish OIDC role, but its trust subject is the separate `rlcosmo/aws-eks-istio-lab` repository. This repository has no deploy trust or deployment workflow, and no tracked Kubernetes manifests/container app sources.
- The nested `cosmotech-infrastructure-mcp` repository remains a separate project and must not be staged or committed through the parent repository.

## Priority backlog

| Priority | Item | Completion evidence |
| --- | --- | --- |
| P0 | Verify GLPI interactive login and practice recovery. | GLPI login and AWS Backup recovery path are exercised. |
| P0 | Resolve legacy `orders` deployments with their owner/configuration. | Restore readiness using an identified source of truth or document an approved retirement; preserve data and queues. |
| P1 | Keep EKS capacity stable and investigate autoscaler RBAC warnings. | All nodes and required pods remain Ready; autoscaler handles pending workloads without repeated forbidden API warnings. |
| P1 | Track the live EKS, Istio, application, and observability state in versioned IaC/manifests. | Drift report reconciled and repeatable validation/deployment path. |
| P1 | Define observability persistence, retention, backups, and recovery. | PVC/storage design and verified restore; avoid relying on ephemeral pod storage. |
| P1 | Implement and test a notification destination. | Controlled alert reaches an approved receiver. |
| P1 | Extend durable order intake into business processing and recovery. | Inventory/payment/fulfillment semantics, retry/DLQ replay tests, and trace propagation are implemented and validated. |
| P1 | Add a DEV-only deployment workflow using GitHub OIDC. | Trust limited to this repository and protected main/environment; IAM permissions reviewed and post-deploy health checks pass. |
| P2 | Expand application, network, and IAM audit coverage. | Least-privilege review, backup restore evidence, endpoint and public exposure tests. |

## Validation recorded

Local project validation passed: 43 pytest tests, `compileall`, `pip check`, Ruff, Terraform formatting and validation, Lambda artifact validation, and Compose configuration syntax. Terraform applied six in-place changes (consumer IAM, both Lambda packages, DynamoDB PITR, and source/DLQ message limits) with zero creates or destroys, then applied the rebuilt Lambda packages with two in-place changes and zero creates or destroys. The signed live API smoke test returned 202 twice for one synthetic order; exactly one matching `RECEIVED` record and a `COMPLETE` idempotency claim were found. Source queue returned to 0; DLQ remained at 1 visible message and was not read or changed. The previously known EKS legacy workload, observability persistence/alerts, GitHub OIDC deployment, GLPI login, and backup recovery gaps remain open.
