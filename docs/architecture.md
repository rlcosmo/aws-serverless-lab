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

### Current Python Scaffold

The current producer validates the API-shaped request and publishes a minimal `order.created` version 1 message. It does not persist the order yet. The consumer validates messages and uses a DynamoDB idempotency adapter when `ORDERS_TABLE_NAME` is configured. Its business processing function remains a seam. The adapter provides a conditional claim and completed-record check for that seam; this does not make real order processing durable or provide exactly-once side effects for future external operations.

The table uses string partition/sort keys `pk` and `sk`. Idempotency records are keyed as `IDEMPOTENCY#<order_id>` / `STATE`; `ORDER#<order_id>` / `ORDER` is reserved for future order records and currently unused. The consumer role can only `GetItem` and `UpdateItem` on the table, constrained by the `IDEMPOTENCY#*` partition-key prefix. The adapter claims with `UpdateItem` conditioned on no prior key or an expired lease, then marks completion conditioned on the unique claim ID. A concurrent duplicate skips only a completed record; a live in-progress claim fails that SQS record for retry. The 120-second claim lease exceeds the current 30-second Lambda timeout, allowing recovery after a killed invocation. Completed records use a 30-day expiry. Only idempotency records should contain numeric `expires_at` (Unix epoch seconds) for TTL; DynamoDB TTL deletion is asynchronous, so logical expiry conditions, not TTL deletion timing, release a claim. After completion expiry, a sufficiently late duplicate can run again. If the claim succeeds but a future external side effect succeeds and completion then fails, a retry can repeat that side effect; such effects must also be idempotent or transactionally coordinated. The current `process_order` is a no-op seam, not durable business processing.

Request limits are 256 KiB for the body, 1–128 characters for `order_id` and each SKU, 1–100 items, and quantities from 1 to 10,000. API Gateway bodies marked Base64 encoded are strictly decoded as UTF-8 before JSON parsing. Event version must be an integer (not a boolean) equal to 1.

## Reliability and Operations

The producer configures bounded SDK retries and short connect/read timeouts for SQS calls. A failed response can be ambiguous: SQS may have accepted a message even when the producer timed out before receiving confirmation. A client retry can therefore publish a duplicate. Once persistence is introduced, use a stable idempotency key and an atomic durable claim/state transition in DynamoDB; do not treat an in-memory cache as sufficient.

The consumer reports failures by SQS message ID so successful records in a batch are not retried. Both invalid/permanent messages and transient processing failures remain failed records: they are retried under the queue's redrive policy and eventually sent to a DLQ rather than being silently discarded. Configure the event source mapping for partial batch responses. A record without a message ID fails the invocation because it cannot be identified in `batchItemFailures`.

Set the SQS visibility timeout with enough margin for the Lambda timeout, batching window, and retries; confirm the final values against the event source mapping configuration before deployment. Bound `maxReceiveCount`, set source and DLQ retention deliberately, alarm on DLQ depth and age, and document who investigates and how replay is authorized. Redrive should be controlled and safe to repeat because a replay may duplicate work.

There is a persistence/publication gap if ingress first writes an order to DynamoDB and then separately publishes to SQS: a crash between operations can leave an order without an event (or a retry can publish twice). Prefer a transactional outbox: write the order and an outbox record atomically, then have a publisher deliver pending outbox records and mark them delivered with retry-safe state. If an outbox is not used, explicitly document and implement reconciliation/compensation; do not claim atomicity across DynamoDB and SQS.

Development log retention defaults to seven days. Three metric alarms cover any invocation error for each Lambda and any visible DLQ message. They have no notification actions in this scaffold, so an operator must inspect CloudWatch alarm state; an alert destination can be introduced after its operations and cost are approved. Each alarm may incur CloudWatch charges. Logs can also incur ingestion and storage charges.

## Security Boundaries

Grant each Lambda role only the actions and resource ARNs it needs: ingress access to the order table and queue send action; worker access to the queue, required table operations, and the specific SNS topic. Scope trust policies to the intended service and function context where supported. Encrypt data in transit and at rest using service encryption defaults or explicitly managed keys as requirements dictate. Keep credentials out of source, Terraform variables, logs, and state; use role-based access and a secrets manager for runtime secrets if needed. Require review of IAM, data retention, and network exposure changes.

## Infrastructure and Change Management

Organize Terraform into small, understandable modules and environments. Pin provider versions, declare required inputs, mark sensitive values, and use remote state with encryption, locking, and restricted access when deployment is approved. Run formatting, validation, security checks, and plan review in the delivery workflow. Do not run `terraform apply` or `terraform destroy` without explicit authorization; this project has not yet initialized Git or provisioned AWS resources.
