# AWS Serverless Lab


## Canonical repositories

This repository is the lab index and preserves migration snapshots. Active ownership is now:

- [Infrastructure / Terraform](https://github.com/rlcosmo/cosmotech-infrastructure-iac) — the only manager of the existing S3 backend/state.
- [Kubernetes RBAC](https://github.com/rlcosmo/cosmotech-kubernetes-rbac).
- [GitOps / Argo CD](https://github.com/rlcosmo/cosmotech-gitops).
- [Orders API / CI](https://github.com/rlcosmo/cosmotech-orders-api).
- [Observability / backups](https://github.com/rlcosmo/cosmotech-observability).
- [GLPI / Kestra Automation](https://github.com/rlcosmo/cosmotech-automation).

All six are private and preserve original commit ancestry. Original files remain as frozen migration snapshots; do not apply Terraform or deploy applications from them. Worker extraction is deferred; the independent MCP repository remains untouched. Some first-party source is retained in IaC as bootstrap/Lambda build snapshots until component artifact references are migrated.

Argo CD: https://argocd.cosmotechsolutions.com.br/ — dedicated private EC2 with K3s, authenticated HTTPS through the existing ALB. GitHub Actions builds/publishes images; Argo CD owns Orders API delivery. Real GMUD/human gates remain mandatory; private-repository protection setup was rejected by the current GitHub plan, so releases remain blocked. See [current execution status](docs/EXECUTION-STATUS.md) and the infrastructure repository README for deploy, backup and rollback procedures.

AWS Serverless Lab is a hands-on lab for operating an event-driven order-processing service with AWS managed services, plus an existing EKS and observability environment. It uses Python 3.12 and Boto3 for application code and Terraform for the serverless resources represented in this repository.

## Architecture

The deployed development environment includes an IAM-authorized HTTP API Gateway route, Lambda, SQS, DynamoDB, EKS, Istio, and an observability stack. GLPI and Kestra run on a private EC2 host and are published through the existing ALB at [glpi.cosmotechsolutions.com.br](https://glpi.cosmotechsolutions.com.br/) and [kestra.cosmotechsolutions.com.br](https://kestra.cosmotechsolutions.com.br/). AWS WAF restricts public hostnames, rate-limits requests, and keeps observability routes restricted to the administrator CIDR. The databases and container ports remain private. See [docs/public-access.md](docs/public-access.md) for DNS, TLS, routing, authentication, logging, and rollback details. Approval-gated change automation prerequisites and current blockers are tracked in [docs/itsm-change-gates.md](docs/itsm-change-gates.md). The Lambda path validates orders, queues versioned events, and stores order records idempotently in DynamoDB. The EKS Orders workloads are separate live deployments whose observed baseline manifests and new candidate container sources are now tracked here. See [docs/architecture.md](docs/architecture.md) for behavior and [docs/initial-audit.md](docs/initial-audit.md) for live evidence and remaining work.

## Repository Layout

```text
docs/          Architecture and delivery roadmap
scripts/       Local development and operational helper scripts
src/           Python 3.12 application and Lambda handlers
terraform/     Terraform infrastructure definitions
tests/         Unit and integration tests
requirements.txt
```

## Prerequisites

- Ubuntu 24.04 LTS on WSL2 or a compatible Linux environment
- Python 3.12 and `venv`
- AWS CLI v2 and Terraform 1.17 for later infrastructure work
- Git for local version control

Do not place AWS access keys, session tokens, private keys, or populated secret files in this repository. Prefer short-lived AWS IAM Identity Center or role-based credentials. CI runs validation; a separate protected DEV workflow obtains short-lived OIDC credentials only after four real approvals.

## Local Development

Create and activate an isolated Python environment, then install the pinned project dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the unit test suite with:

```bash
python -m pytest
```

The producer uses `ORDERS_QUEUE_URL` for its SQS destination. Tests run locally with Moto and do not connect to AWS. The consumer requires `ORDERS_TABLE_NAME`, stores orders in DynamoDB, and uses conditional idempotency claims. The live API → SQS → Lambda → DynamoDB flow was smoke-tested with a synthetic order; submitting the same order twice persisted one matching record. The current deployed Lambda path stores intake with `RECEIVED` status. A complete simulated processing candidate is tested but not deployed; see [orders processing](docs/orders-processing.md).

### Lambda Artifacts

Build and validate both deployment ZIPs with Python 3.12:

```bash
python scripts/build_lambda_artifacts.py
python scripts/validate_lambda_artifacts.py
```

The deterministic archives contain only first-party `.py` files from `src/`. They omit pytest, Moto, and SDK packages; the handlers use the boto3/botocore SDK included in the AWS Lambda Python 3.12 runtime. `dist/` is ignored by Git. Rebuild after changing application code and before Terraform validation; Terraform expects both ZIP paths to exist.

Build Lambda archives before Terraform planning so it uses the current source. Run Terraform formatting and static validation locally. The DEV backend is an encrypted, versioned, access-restricted S3 bucket with native state locking; use `-backend=false` for local validation that must not read remote state:

```bash
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform/environments/dev init -backend=false -input=false
terraform -chdir=terraform/environments/dev validate
```

Terraform backend initialization uses the repository's S3 backend and requires AWS access. Validation can use `-backend=false`; do not commit state, plan files, credentials, or local backups. The `.terraform.lock.hcl` provider lock file is a source artifact that should be versioned.

### Cost Notes

AWS resource usage incurs variable charges. The account is currently on the paid plan with promotional credits available. The lab includes EKS, Spot workers, NAT, load balancers, CloudWatch, and a private `t3.large` ITSM host with encrypted gp3 storage and AWS Backup. See the execution report for current costs and verified SNS delivery. No cost ceiling was applied per the current project instruction.

## Delivery Plan

GitHub Actions validates Python, Lambda artifacts and Terraform. The DEV deployment candidate requires four protected environments reviewed by `rlcosmo`, scoped OIDC and signed GLPI evidence. Full change integration remains disabled pending independent Kestra authentication and a GitHub App. Five observability components now use encrypted Retain PVCs with tested isolated restoration. See [execution status](docs/EXECUTION-STATUS.md), [recovery](docs/observability-recovery.md), and [remaining work](docs/roadmap.md).
