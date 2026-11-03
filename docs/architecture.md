# Architecture

## Purpose and Scope

This document distinguishes the implemented serverless path from the intended end state. The development AWS environment is deployed. Terraform in this repository manages the serverless API, Lambda, SQS, DynamoDB, and CloudWatch resources; the live EKS and observability stack is not currently declared here. Review plans and assess cost, data, and security impact before infrastructure changes.

## Logical Components

- **Amazon API Gateway HTTP API:** exposes `POST /orders`; the route uses AWS IAM authorization and requires SigV4-signed requests with `execute-api:Invoke` permission.
- **Producer Lambda (Python 3.12, Boto3):** validates the request and publishes a minimal `order.created` event to SQS. It does not write order records to DynamoDB.
- **Amazon DynamoDB:** the current table supports conditional idempotency claims for the consumer. Durable order state is not implemented.
- **Amazon SQS:** buffers work and retries failed records through a redrive policy and DLQ.
- **Consumer Lambda (Python 3.12, Boto3):** validates messages and records idempotency claims. The `process_order` business function remains a no-op seam.
- **Amazon CloudWatch:** collects Lambda logs, a dashboard, and error/DLQ alarms. Current Terraform alarms do not have notification actions.
- **Terraform:** defines infrastructure as reviewable, version-controlled code. State and plan artifacts are sensitive operational data and must not be committed.

## Order Processing Flow

1. A client signs a `POST /orders` request with AWS SigV4; API Gateway rejects anonymous requests before Lambda invocation.
2. The producer validates the request and publishes a minimal versioned order event to SQS.
3. SQS invokes the consumer Lambda with partial batch failure reporting. Failed records can be retried and eventually sent to the DLQ.
4. The consumer validates each event and uses a conditional DynamoDB claim to suppress duplicate completed work. The current business processing step is a no-op seam; the flow does not yet persist order state or cause a business side effect.
5. CloudWatch logs, metrics, dashboard, and alarms support troubleshooting. Alarms currently have no notification destination configured by this repository.

The target API → SQS → worker → DynamoDB flow is therefore only partially implemented. Do not describe it as end-to-end durable order processing until the persistence, business operation, retries, and recovery path are implemented and tested.

### Current Python Scaffold

The current producer validates the API-shaped request and publishes a minimal `order.created` version 1 message. It does not persist the order yet. The consumer validates messages and uses a DynamoDB idempotency adapter when `ORDERS_TABLE_NAME` is configured. Its business processing function remains a seam. The adapter provides a conditional claim and completed-record check for that seam; this does not make real order processing durable or provide exactly-once side effects for future external operations.

The table uses string partition/sort keys `pk` and `sk`. Idempotency records are keyed as `IDEMPOTENCY#<order_id>` / `STATE`; `ORDER#<order_id>` / `ORDER` is reserved for future order records and currently unused. The consumer role can only `GetItem` and `UpdateItem` on the table, constrained by the `IDEMPOTENCY#*` partition-key prefix. The adapter claims with `UpdateItem` conditioned on no prior key or an expired lease, then marks completion conditioned on the unique claim ID. A concurrent duplicate skips only a completed record; a live in-progress claim fails that SQS record for retry. The 120-second claim lease exceeds the current 30-second Lambda timeout, allowing recovery after a killed invocation. Completed records use a 30-day expiry. Only idempotency records should contain numeric `expires_at` (Unix epoch seconds) for TTL; DynamoDB TTL deletion is asynchronous, so logical expiry conditions, not TTL deletion timing, release a claim. After completion expiry, a sufficiently late duplicate can run again. If the claim succeeds but a future external side effect succeeds and completion then fails, a retry can repeat that side effect; such effects must also be idempotent or transactionally coordinated. The current `process_order` is a no-op seam, not durable business processing.

Request limits are 256 KiB for the body, 1–128 characters for `order_id` and each SKU, 1–100 items, and quantities from 1 to 10,000. API Gateway bodies marked Base64 encoded are strictly decoded as UTF-8 before JSON parsing. Event version must be an integer (not a boolean) equal to 1.

## Reliability and Operations

The producer configures bounded SDK retries and short connect/read timeouts for SQS calls. A failed response can be ambiguous: SQS may have accepted a message even when the producer timed out before receiving confirmation. A client retry can therefore publish a duplicate. Once persistence is introduced, use a stable idempotency key and an atomic durable claim/state transition in DynamoDB; do not treat an in-memory cache as sufficient.

The consumer reports failures by SQS message ID so successful records in a batch are not retried. Both invalid/permanent messages and transient processing failures remain failed records: they are retried under the queue's redrive policy and eventually sent to a DLQ rather than being silently discarded. Configure the event source mapping for partial batch responses. A record without a message ID fails the invocation because it cannot be identified in `batchItemFailures`.

Set the SQS visibility timeout with enough margin for the Lambda timeout, batching window, and retries; confirm the final values against the event source mapping configuration before deployment. Bound `maxReceiveCount`, set source and DLQ retention deliberately, alarm on DLQ depth and age, and document who investigates and how replay is authorized. Redrive should be controlled and safe to repeat because a replay may duplicate work.

When durable order persistence is implemented, address the persistence/publication gap: writing to DynamoDB and then separately publishing to SQS can leave an order without an event or publish duplicates after retries. Prefer a transactional outbox, or implement and document reconciliation/compensation. Do not claim atomicity across DynamoDB and SQS.

Development log retention defaults to seven days. Three metric alarms cover any invocation error for each Lambda and any visible DLQ message. The Terraform alarms have no notification actions, so operators must inspect CloudWatch alarm state. Add and validate a notification destination before treating alerting as operational; account for its cost. Logs also incur ingestion and storage charges.

## Security Boundaries

Grant each Lambda role only the actions and resource ARNs it needs: the producer sends messages to its SQS queue; the consumer reads/deletes messages and accesses the idempotency table. Scope trust policies to the intended service and function context where supported. Encrypt data in transit and at rest using service encryption defaults or explicitly managed keys as requirements dictate. Keep credentials out of source, Terraform variables, logs, and state; use role-based access and a secrets manager for runtime secrets if needed. Require review of IAM, data retention, and network exposure changes.

## Infrastructure and Change Management

Terraform is organized into modules under `terraform/modules` and the `dev` environment. Terraform state and plan artifacts are sensitive and must not be committed. Run formatting, validation, security checks, and a full plan review before deployment. Never run `terraform destroy`; assess budget and data impact before any apply.
