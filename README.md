# AWS Serverless Lab

AWS Serverless Lab is a hands-on reference project for designing and operating an event-driven order-processing service with AWS managed services. It uses Python 3.12 and Boto3 for application code and Terraform for infrastructure definitions.

## Architecture

The planned system uses AWS Lambda, Amazon DynamoDB, Amazon SQS, Amazon SNS, and Amazon CloudWatch. An API-facing Lambda validates and stores an order, then publishes an event to SQS. A worker Lambda consumes the event, performs processing, updates order state, and publishes an outcome notification through SNS. CloudWatch provides centralized logs, metrics, and alarms. See [docs/architecture.md](docs/architecture.md) for the flow and operational considerations.

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

Run the current test suite with:

```bash
python -m pytest
```

Run Terraform formatting and static validation from the infrastructure directory when Terraform configuration is present:

```bash
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform validate
```

Terraform validation may require `terraform init` after configuration is added. Review and approve a plan before any deployment. Never run `terraform apply` or `terraform destroy` without explicit project authorization.

## Delivery Plan

See [docs/roadmap.md](docs/roadmap.md) for the three-week implementation plan. The project should advance through reviewed, testable increments with operational readiness and security checks included throughout.
