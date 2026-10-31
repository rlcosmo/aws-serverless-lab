# AWS Serverless Lab

AWS Serverless Lab is a hands-on reference project for designing and operating an event-driven order-processing service with AWS managed services. It uses Python 3.12 and Boto3 for application code and Terraform for infrastructure definitions.

## Architecture

The current development infrastructure contains AWS Lambda, Amazon DynamoDB, Amazon SQS, and Amazon CloudWatch. It does not define API Gateway, SNS, NAT Gateway, EC2, or RDS. See [docs/architecture.md](docs/architecture.md) for the flow and operational considerations.

This repository is an initial scaffold. No AWS resources have been created, and no deployment has been performed.

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

Do not place AWS access keys, session tokens, private keys, or populated secret files in this repository. Prefer short-lived AWS IAM Identity Center or role-based credentials when cloud access is eventually authorized.

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

The producer uses `ORDERS_QUEUE_URL` for its SQS destination. Tests run locally with Moto and do not connect to AWS. The consumer now uses a conditional DynamoDB idempotency claim when `ORDERS_TABLE_NAME` is configured. Its business processing function remains a seam, so this does not yet make real order processing durable.

### Lambda Artifacts

Build and validate both deployment ZIPs with Python 3.12:

```bash
python scripts/build_lambda_artifacts.py
python scripts/validate_lambda_artifacts.py
```

The deterministic archives contain only first-party `.py` files from `src/`. They omit pytest, Moto, and SDK packages; the handlers use the boto3/botocore SDK included in the AWS Lambda Python 3.12 runtime. `dist/` is ignored by Git. Rebuild after changing application code and before Terraform validation; Terraform expects both ZIP paths to exist.

Run Terraform formatting and static validation from the infrastructure directory when Terraform configuration is present:

```bash
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform validate
```

Terraform validation requires provider initialization. In this phase, validation is local and must not access AWS; no plan, apply, or destroy is part of the build process. The local state path is `terraform/environments/dev/terraform.tfstate`; it and its backups/plans are ignored. Protect local state with filesystem permissions and encrypted, access-controlled backups outside the repository. To recover, restore a verified backup to that exact path while Terraform is stopped, preserve the prior state copy, and inspect state/configuration consistency before any later operation. Do not create a cloud backend in this phase. The `.terraform.lock.hcl` provider lock file is a source artifact that should be versioned.

### Cost Notes

These AWS services are not asserted to be free. Potential charges include Lambda requests and duration; SQS requests and data transfer; DynamoDB on-demand reads/writes and stored data; CloudWatch log ingestion/storage and three metric alarms (one per Lambda plus one DLQ alarm). Seven-day log retention limits stored history but does not remove ingestion charges. DynamoDB point-in-time recovery is disabled by default; enabling it can add charges. The small number of alarms is intended to alert on function failures and any visible DLQ message; each alarm can incur a recurring CloudWatch charge. No notification topic or API endpoint is configured.

## Delivery Plan

See [docs/roadmap.md](docs/roadmap.md) for the three-week implementation plan. The project should advance through reviewed, testable increments with operational readiness and security checks included throughout.
