# Initial environment audit

Audit date: 2026-11-03 (UTC). This is a point-in-time, read-only inventory except for the documented API Gateway authorization correction. Resource values, endpoints, IP addresses, and secret contents are intentionally omitted.

## Scope and evidence

The audit used AWS CLI and Cost Explorer, Kubernetes and Helm read-only queries, Terraform validation/plan, the CosmoTech Infrastructure MCP inventory and health tools, and the repository source. It did not read DynamoDB item bodies, Kubernetes Secret data, or the body of any SQS message. No existing resources or application data were removed.

## Live inventory

| Area | Observed state |
| --- | --- |
| AWS | Correct target account and `us-east-1` region. One active EKS cluster on Kubernetes 1.37; one NAT Gateway; two Spot EKS worker instances; two load balancers (an internal NLB and an internet-facing ALB). |
| Serverless | One HTTP API, two Lambda functions, four SQS queues (two source/DLQ pairs), two DynamoDB tables, two ECR repositories, and CloudWatch logs, dashboard, and alarms. |
| API security | The `POST /orders` route was open to anonymous callers at audit start. Terraform now requires `AWS_IAM` authorization. An unsigned request returned HTTP 403; no authenticated order was submitted. |
| SQS | One existing serverless DLQ contains one message. The message was not read, deleted, or replayed. Other queue counts were zero at audit time. |
| DynamoDB | Both tables use on-demand capacity. One has 3 items and one has 62. Point-in-time recovery was disabled on both; TTL was enabled only on the serverless table. Item contents were not read. |
| EKS workloads | Two worker nodes were Ready. At one sample, node memory was 39% and 82%. The active `orders-api` and `orders-worker` namespaces were reported healthy by the health check; separate older API and worker pods in namespace `orders` were unready, with the worker in CrashLoopBackOff (91 restarts). These legacy workloads were left untouched pending ownership and impact analysis. |
| Kubernetes persistence | No PVCs were present. Loki, Prometheus, Alertmanager, and Tempo StatefulSets had no volume claim templates at audit time. Their data persistence and recovery are not established. |
| Observability | Helm reported Alloy, AWS Load Balancer Controller, Kyverno, Loki, OpenTelemetry Collector, Prometheus stack, and Tempo deployed. The MCP health check reported the observability components healthy. Alert delivery to a functioning notification destination was not verified. |
| Exposure | An internet-facing ALB is associated with observability ingress. TLS validation and application authentication could not be confirmed, so treat both as open security findings until verified. Detailed routing and access-path data are omitted from this public repository. The EKS API is public with a restricted source range. Exact addresses are omitted. |
| Infrastructure as code | Terraform in this repository manages the serverless stack. No EKS, GLPI/Kestra EC2, or observability infrastructure definitions were found in the repository. The `kubernetes/` directory has no tracked manifests. The live EKS and observability infrastructure therefore cannot be reproduced from this repository today. |
| CI/CD | No GitHub Actions workflow files were found. |
| GLPI/Kestra | No dedicated EC2 instance exists. Neither application was installed. |

## Budget gate

Cost Explorer returned zero billed cost while its usage data showed active services; this is not sufficient evidence that the environment is free or below budget. The account's existing monthly budget is set to $1 and currently reports no spend, which also does not prove the requested $100 cap is met.

Using a 730-hour month and current public us-east-1 list rates, the known always-on floor is:

| Existing item | Calculation | Monthly floor |
| --- | --- | ---: |
| EKS standard-support control plane | $0.10/hour × 730 | $73.00 |
| NAT Gateway hourly charge | $0.045/hour × 730 | $32.85 |
| One public IPv4 address | $0.005/hour × 730 | $3.65 |
| **Known existing floor** | Excludes worker compute, load balancers, EBS, data processing/transfer, logs, and application usage | **$109.50** |

This lower bound already exceeds the $100/month ceiling. An additional always-on `t3.large` and 50 GiB gp3 volume would add at least about $64.74/month using the current us-east-1 Linux price-list rate of $0.0832/hour and $0.08/GB-month, before networking, snapshots, or application usage. A smaller instance would not solve the existing budget overrun and has not been capacity-tested.

Therefore no EC2, GLPI, Kestra, EBS, NAT, endpoint, backup, or other cost-bearing resource was created. To proceed with the required ITSM host, first reconcile actual billing and reduce the existing environment's recurring floor through an owner-approved cost plan, or raise the lab budget. Do not leave the budget gate until the full bill, including usage and Spot variation, is understood.

Public pricing references: [EKS](https://aws.amazon.com/eks/pricing/), [VPC and NAT Gateway](https://aws.amazon.com/vpc/pricing/), [public IPv4](https://aws.amazon.com/vpc/pricing/), [EC2 T3](https://aws.amazon.com/ec2/instance-types/t3/), [EBS gp3](https://aws.amazon.com/ebs/general-purpose/).

## Changes made

- Set the existing API Gateway route to `AWS_IAM` in Terraform and applied that one in-place update. The plan was `0 add, 1 change, 0 destroy`; an anonymous request returned 403. AWS documents HTTP API IAM authorization as SigV4 plus `execute-api` permission: [AWS documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control-iam.html).
- Updated the README and architecture document to reflect deployed resources and current implementation gaps instead of claiming that no resources exist.
- No other AWS or Kubernetes resources were changed.

## Prioritized backlog

| Priority | Work | Gate / acceptance evidence |
| --- | --- | --- |
| P0 | Reconcile actual monthly cost and bring the whole lab under the $100 ceiling. | Explain Cost Explorer's zero-dollar data, include current worker/ELB/EBS/NAT transfer and service usage; verify full monthly projection before adding resources. |
| P0 | Verify and protect public Grafana access. | Confirm login/authentication, TLS behavior, and allowed client access; retain a working administrator path and verify with anonymous and authenticated checks. |
| P1 | Decide ownership and safely repair or retire the two stale `orders` namespace pods. | Identify managing source and dependencies first; test the active service path before any scaling or rollout. |
| P1 | Define persistence, retention, and recovery for Prometheus, Alertmanager, Loki, and Tempo. | Reviewed storage cost, backups/restore evidence, and retention settings. Current StatefulSets have no PVCs. |
| P1 | Add a real alert receiver and test delivery. | A controlled test alert reaches an approved destination; no working destination is currently verified. |
| P1 | Implement durable Orders processing and recovery. | Persist order state, define idempotent business side effects, exercise retries and DLQ recovery, and test API → SQS → worker → DynamoDB. |
| P1 | Add repeatable EKS and observability IaC/manifests and reconcile them against the live cluster. | Plans/manifests account for all live resources and a fresh environment can be reproduced without manual hidden state. |
| P1 | Add CI checks and deployment gates. | Lint, tests, Terraform/Kubernetes validation, image build, and an authorized DEV-only deploy with health checks. |
| P2 | Deploy GLPI and Kestra on the dedicated EC2 requested by the mission. | Only after budget gate, private access/SSM, IAM, backup/recovery, TLS ingress, and capacity test pass. Keep GLPI and Kestra off EKS. |
| P2 | Add IAM/backup and audit evidence for the application data. | Least-privilege review, point-in-time recovery decision, retention policy, and tested recovery procedure. |

## Local validation

- `python -m pytest -q` using the existing `.venv`: 38 passed.
- `python3 -m compileall -q src tests`: passed.
- `python3 -m pip check`: passed.
- `terraform fmt -check -recursive`: passed.
- `terraform validate`: passed.
- Full Terraform plan after the API change: no changes.
- Ruff: passed (`ruff check .`; Ruff was installed into the ignored local `.venv`).
- Docker CLI is present, but the repository has no Dockerfile or Compose file to build.
