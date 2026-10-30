# Repository Guidelines

## Project Structure

Application code belongs in `src/`, tests in `tests/`, helper scripts in `scripts/`, Terraform in `terraform/`, and technical documentation in `docs/`. Keep Lambda handlers thin; place reusable business logic and AWS access behind small modules. Python runtime target is 3.12.

## Development Commands

Create a local environment with `python3.12 -m venv .venv`, activate it, and install dependencies with `python -m pip install -r requirements.txt`. Run tests with `python -m pytest`. Format-check infrastructure with `terraform -chdir=terraform fmt -check -recursive` and validate it with `terraform -chdir=terraform validate` after configuration and initialization are available. Do not install tools without project authorization.

## Code and Test Conventions

Use four spaces for Python indentation, descriptive `snake_case` names, type hints for public interfaces, and small functions with explicit error handling. Keep AWS clients injectable where practical so business logic can be tested without AWS. Name tests `test_*.py` and test success, invalid input, retries, duplicate delivery, and failure paths. Keep Terraform formatted, use descriptive resource names, consistent tags, explicit provider constraints, and small modules.

## Reliability and Security

Design handlers for at-least-once delivery: make processing idempotent, bound retries, configure visibility timeouts and DLQs deliberately, and emit structured logs and actionable metrics. Apply least privilege to every IAM role; scope actions and resource ARNs to the function's needs. Never commit AWS credentials, tokens, private keys, `.env` files, Terraform state, plans, or secrets. Use role-based short-lived credentials for authorized cloud work and keep sensitive values out of logs and state.

## Infrastructure Change Controls

Review Terraform formatting, validation, security findings, and plans before deployment. This repository has not provisioned AWS resources. Never run `terraform apply` or `terraform destroy`, access AWS, or create cloud resources without explicit authorization. Do not reinitialize Git or alter remotes/history without project-owner authorization. Document operational assumptions, alarms, recovery steps, and data retention decisions alongside implementation changes.

## Commit Messages

Use Conventional Commits with a lowercase type and concise imperative description: `<type>(<optional-scope>): <description>`. Common types include `feat`, `fix`, `docs`, `test`, `refactor`, `build`, and `chore`. Examples: `docs: initialize AWS serverless lab` and `feat(orders): validate order requests`.

## Pull Requests

Use a concise imperative title, describe behavior and operational impact, link related work when available, and report relevant local validation. Include screenshots only for user-facing visual changes. Call out IAM, data model, retry, observability, and cost changes explicitly.
