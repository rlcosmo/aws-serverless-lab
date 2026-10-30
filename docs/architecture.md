# Architecture

## Purpose and Scope

This document describes the target architecture for an event-driven order-processing lab. The repository is currently a scaffold: AWS resources have not been created. Infrastructure changes must be reviewed through Terraform plans and deployed only with explicit authorization.

## Logical Components

- **Ingress Lambda (Python 3.12, Boto3):** validates the request, assigns or validates an order identifier, stores the initial order, and publishes an order event to SQS.
- **Amazon DynamoDB:** stores order state with a stable partition key such as `order_id`. Access patterns and any secondary indexes must be documented before schema changes.
- **Amazon SQS:** buffers work between ingress and processing, absorbs traffic bursts, and enables retry-based decoupling.
- **Worker Lambda (Python 3.12, Boto3):** consumes messages in batches, processes each order idempotently, updates its state, and publishes a result event.
- **Amazon SNS:** distributes processing outcomes to explicitly configured subscribers. Message content must not include secrets or unnecessary personal data.
- **Amazon CloudWatch:** collects structured Lambda logs, service metrics, dashboards, and actionable alarms for errors, throttles, queue age, and dead-letter queue depth.
- **Terraform:** defines infrastructure as reviewable, version-controlled code. State and plan artifacts are sensitive operational data and must not be committed.

## Order Processing Flow

1. A client request reaches the ingress Lambda through a future API integration.
2. The handler validates required fields and rejects malformed input before persistence.
3. The handler writes an order in `PENDING` state to DynamoDB, using conditional writes or another concurrency-safe strategy where appropriate.
4. It publishes an order event to SQS. The message carries an order identifier and a versioned event type; avoid copying unnecessary customer data into the queue.
5. SQS invokes the worker Lambda. The worker validates the event, loads the authoritative order, and performs idempotent processing so retries do not duplicate effects.
6. On success, the worker updates the order state and publishes a result event to SNS.
7. On a transient failure, the message is retried according to a bounded redrive policy. After the configured receive threshold, SQS moves it to a dead-letter queue (DLQ) for investigation and controlled replay.
8. CloudWatch logs and metrics support troubleshooting and alarms. Logs must be structured, useful, and scrubbed of credentials, tokens, and sensitive payloads.

## Reliability and Operations

Use explicit timeouts, bounded retries, SQS visibility timeouts sized for Lambda processing, batch failure reporting, and a DLQ with an owner and runbook. Define alarms with actionable thresholds and avoid alerting on transient noise. Monitor queue age and DLQ depth in addition to Lambda errors and throttles. Document recovery and replay procedures before production-like use.

## Security Boundaries

Grant each Lambda role only the actions and resource ARNs it needs: ingress access to the order table and queue send action; worker access to the queue, required table operations, and the specific SNS topic. Scope trust policies to the intended service and function context where supported. Encrypt data in transit and at rest using service encryption defaults or explicitly managed keys as requirements dictate. Keep credentials out of source, Terraform variables, logs, and state; use role-based access and a secrets manager for runtime secrets if needed. Require review of IAM, data retention, and network exposure changes.

## Infrastructure and Change Management

Organize Terraform into small, understandable modules and environments. Pin provider versions, declare required inputs, mark sensitive values, and use remote state with encryption, locking, and restricted access when deployment is approved. Run formatting, validation, security checks, and plan review in the delivery workflow. Do not run `terraform apply` or `terraform destroy` without explicit authorization; this project has not yet initialized Git or provisioned AWS resources.
