# AWS Serverless Lab

AWS Serverless Lab is a hands-on lab for operating an event-driven order-processing service with AWS managed services, plus an existing EKS and observability environment. It uses Python 3.12 and Boto3 for application code and Terraform for the serverless resources represented in this repository.

## Architecture

The deployed development environment includes an IAM-authorized HTTP API Gateway route, Lambda, SQS, DynamoDB, EKS, Istio, and an observability stack. GLPI and Kestra run on a private EC2 host and are published through the existing ALB at [glpi.cosmotechsolutions.com.br](https://glpi.cosmotechsolutions.com.br/) and [kestra.cosmotechsolutions.com.br](https://kestra.cosmotechsolutions.com.br/). AWS WAF restricts public hostnames, rate-limits requests, and keeps observability routes restricted to the administrator CIDR. The databases and container ports remain private. See [docs/public-access.md](docs/public-access.md) for DNS, TLS, routing, authentication, logging, and rollback details. Approval-gated change automation prerequisites and current blockers are tracked in [docs/itsm-change-gates.md](docs/itsm-change-gates.md). The Lambda path validates orders, queues versioned events, and stores order records idempotently in DynamoDB. The EKS Orders workloads are separate live deployments whose source manifests are not yet tracked here. See [docs/architecture.md](docs/architecture.md) for behavior and [docs/initial-audit.md](docs/initial-audit.md) for live evidence and remaining work.

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

Do not place AWS access keys, session tokens, private keys, or populated secret files in this repository. Prefer short-lived AWS IAM Identity Center or role-based credentials. CI currently runs validation only and has no AWS deployment credentials.

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

The producer uses `ORDERS_QUEUE_URL` for its SQS destination. Tests run locally with Moto and do not connect to AWS. The consumer requires `ORDERS_TABLE_NAME`, stores orders in DynamoDB, and uses conditional idempotency claims. The live API → SQS → Lambda → DynamoDB flow was smoke-tested with a synthetic order; submitting the same order twice persisted one matching record. This path stores order intake with `RECEIVED` status. It does not implement inventory, payments, or fulfillment.

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

AWS resource usage incurs variable charges. The account is currently on the paid plan with promotional credits available. The lab includes EKS, Spot workers, NAT, load balancers, CloudWatch, and a private `t3.large` ITSM host with encrypted gp3 storage and AWS Backup. See the audit for limits and unimplemented alert delivery. No cost ceiling was applied per the current project instruction.

## Delivery Plan

GitHub Actions runs Python lint/tests, Lambda artifact checks, and Terraform formatting/validation. It does not deploy: EKS and observability manifests are not maintained in this repository and no least-privilege GitHub OIDC deploy role has been configured. See [docs/roadmap.md](docs/roadmap.md) for remaining work.
