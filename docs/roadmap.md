# Three-Week Implementation Roadmap

This roadmap assumes focused, reviewable increments. Each week ends with working local evidence and a documented review; cloud deployment is outside scope until separately authorized.

## Week 1 — Foundations and Contracts

- Define order and event schemas, validation rules, state transitions, and error responses.
- Establish Python 3.12 package layout, configuration boundaries, structured logging conventions, and handler interfaces.
- Implement ingress and worker logic behind testable interfaces; add unit tests using local AWS service mocks where appropriate.
- Define Terraform project layout, provider/version constraints, naming and tagging conventions, and environment inputs without provisioning resources.
- Review data classification, retention needs, and the initial threat model.

**Exit criteria:** documented contracts, reproducible local setup, baseline unit tests, and reviewed Terraform structure.

## Week 2 — Event-Driven Processing and Least Privilege

- Define DynamoDB table keys and required access patterns; implement repository operations and conditional state updates.
- Add SQS queue, redrive policy, DLQ, Lambda event source mapping, and partial batch failure handling to Terraform.
- Implement idempotent processing, bounded retries, input validation, and SNS outcome publishing.
- Write narrowly scoped IAM policies for each function and resource; verify that permissions match actual code paths.
- Add integration tests for successful processing, retries, duplicate delivery, and DLQ routing using local emulation.

**Exit criteria:** end-to-end processing is covered locally, duplicate delivery is safe, and permissions and failure paths have been reviewed.

## Week 3 — Observability and Operational Readiness

- Add structured CloudWatch logs, key service metrics, dashboards, and actionable alarms.
- Document timeout, concurrency, batch size, visibility timeout, retention, and cost assumptions.
- Prepare operational runbooks for queue backlog, DLQ inspection/replay, failed notifications, and incident triage.
- Complete security review for secrets handling, encryption, IAM scope, Terraform state, and sensitive logging.
- Run formatting, tests, Terraform formatting/validation, and static security checks; capture results for review.
- Prepare a deployment plan for approval without applying it.

**Exit criteria:** reviewed operational documentation, recorded validation results, and a human-reviewed infrastructure plan. No AWS resources are created until separately authorized.
