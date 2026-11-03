# Architecture

## Purpose and Scope

This document distinguishes the implemented serverless path from the intended end state. Terraform manages the serverless API, Lambda, SQS, DynamoDB, CloudWatch resources, the private GLPI/Kestra host, and the DEV S3 state backend. The live EKS and observability stacks are still not declared here. Review plans and assess data, security, and operational impact before infrastructure changes.

The ITSM host runs Ubuntu 24.04 on a private `t3.large` with encrypted 50 GiB gp3 storage, no public IP or ingress rules, and SSM access. Docker Compose runs GLPI with a dedicated MariaDB and Kestra with a dedicated PostgreSQL. Application ports are bound to loopback and accessed through SSM port forwarding. AWS Backup retains daily EC2 recovery points for 14 days. See [the host runbook](../ops/itsm/README.md).

## Logical Components

- **Amazon API Gateway HTTP API:** exposes `POST /orders`; the route uses AWS IAM authorization and requires SigV4-signed requests with `execute-api:Invoke` permission.
- **Producer Lambda (Python 3.12, Boto3):** validates the request and publishes a version 2 `order.created` event with the complete order payload and a UTC creation timestamp.
- **Amazon DynamoDB:** stores order records and conditional consumer idempotency claims in the `pk`/`sk` table. Point-in-time recovery is enabled for the serverless Orders table.
- **Amazon SQS:** buffers work and retries failed records through a redrive policy and DLQ.
- **Consumer Lambda (Python 3.12, Boto3):** validates version 2 messages, claims the order ID, and conditionally persists the order record. Repeated identical deliveries are accepted; reuse of an order ID with different items is sent to the DLQ.
- **Amazon CloudWatch:** collects Lambda logs, a dashboard, and error/DLQ alarms. Current Terraform alarms do not have notification actions.
- **Terraform:** defines infrastructure as reviewable, version-controlled code. State and plan artifacts are sensitive operational data and must not be committed.
- **Terraform state:** DEV uses a versioned, encrypted S3 bucket with public access blocked, TLS-only access, and native lock files. The bucket and host instance have `prevent_destroy` safeguards.
- **ITSM host:** private, SSM-only access to GLPI and Kestra; generated credentials are stored in SSM SecureString and not available to the instance role for retrieval.

## Order Processing Flow

1. A client signs a `POST /orders` request with AWS SigV4; API Gateway rejects anonymous requests before Lambda invocation.
2. The producer validates the request and publishes a version 2 event containing the normalized order and UTC creation timestamp to SQS.
3. SQS invokes the consumer Lambda with partial batch failure reporting. Failed records can be retried and eventually sent to the DLQ.
4. The consumer validates the complete event, takes a lease-based conditional idempotency claim, and conditionally writes `ORDER#<order_id>/ORDER` with the item list and `RECEIVED` status. The order write and idempotency completion use separate DynamoDB calls; retries reconcile safely by comparing the existing order payload.
5. CloudWatch logs, metrics, dashboard, and alarms support troubleshooting. Alarms currently have no notification destination configured by this repository.

The API → SQS → Lambda consumer → DynamoDB persistence path is implemented for new version 2 events. The EKS `orders-api` and `orders-worker` deployments use a separate queue and remain outside this repository's source of truth; see the live audit for their status. This workflow records orders but does not implement inventory reservation, payment, or fulfillment.

### Current Python Scaffold

The producer validates the API-shaped request and publishes an `order.created` version 2 message containing the normalized order and UTC timestamp. The consumer requires `ORDERS_TABLE_NAME`, persists the normalized order to DynamoDB, and returns partial batch failures for invalid, transient, or conflicting records. The versioned idempotency key avoids collisions with earlier development claims created before order persistence was implemented.

The table uses string partition/sort keys `pk` and `sk`. Idempotency records use `IDEMPOTENCY#V2#<order_id>` / `STATE`; order records use `ORDER#<order_id>` / `ORDER`. The consumer role can read/update only the idempotency key prefix and read/create only the order key prefix. A claim uses a conditional update when no record exists or its lease has expired, then marks completion with the unique claim ID. The 120-second claim lease exceeds the 30-second Lambda timeout. Completed claims expire after 30 days; DynamoDB TTL deletion is asynchronous, so conditional lease expiry—not TTL timing—controls recovery. Order records have no TTL and stay available for late duplicate verification. The order put and claim completion are separate operations, so a retry after a partial failure verifies the existing order payload before completing safely. No external side effect beyond this DynamoDB write is currently performed.

Request limits are 256 KiB for the body, 1–128 characters for `order_id` and each SKU, 1–100 items, and quantities from 1 to 10,000. API Gateway bodies marked Base64 encoded are strictly decoded as UTF-8 before JSON parsing. Event version must be an integer (not a boolean) equal to 2. Both SQS queues accept messages up to 1 MiB to allow for the event envelope around a maximum-sized validated request.

## Reliability and Operations

The producer configures bounded SDK retries and short connect/read timeouts for SQS calls. A failed response can be ambiguous: SQS may have accepted a message even when the producer timed out before receiving confirmation. A client retry can therefore publish a duplicate. Consumer idempotency protects the DynamoDB order write, but API publication is not deduplicated and there is no transactional outbox. This system records order intake; it does not claim end-to-end fulfillment.

The consumer reports failures by SQS message ID so successful records in a batch are not retried. Both invalid/permanent messages and transient processing failures remain failed records: they are retried under the queue's redrive policy and eventually sent to a DLQ rather than being silently discarded. Configure the event source mapping for partial batch responses. A record without a message ID fails the invocation because it cannot be identified in `batchItemFailures`.

Set the SQS visibility timeout with enough margin for the Lambda timeout, batching window, and retries; confirm the final values against the event source mapping configuration before deployment. Bound `maxReceiveCount`, set source and DLQ retention deliberately, alarm on DLQ depth and age, and document who investigates and how replay is authorized. Redrive should be controlled and safe to repeat because a replay may duplicate work.

The producer publishes to SQS before the consumer writes DynamoDB. A client retry may publish the same event more than once, which is handled idempotently by the consumer. There is no transactional outbox or deduplication at the API boundary; monitor and investigate delivery failures using Lambda metrics, SQS depth, and the DLQ. Do not claim atomicity across API Gateway, SQS, and DynamoDB.

Development log retention defaults to seven days. Three metric alarms cover any invocation error for each Lambda and any visible DLQ message. The Terraform alarms have no notification actions, so operators must inspect CloudWatch alarm state. Add and validate a notification destination before treating alerting as operational. Logs also incur ingestion and storage charges.

## Security Boundaries

Grant each Lambda role only the actions and resource ARNs it needs: the producer sends messages to its SQS queue; the consumer reads/deletes messages and may read/update `IDEMPOTENCY#*` and read/create `ORDER#*` records in the Orders table. Scope trust policies to the intended service and function context where supported. DynamoDB point-in-time recovery is enabled for the Orders table. Keep credentials out of source, Terraform variables, logs, and state; use role-based access and a secrets manager for runtime secrets if needed. Require review of IAM, data retention, and network exposure changes.

## Infrastructure and Change Management

Terraform is organized into modules under `terraform/modules` and the `dev` environment. Terraform state and plan artifacts are sensitive and must not be committed. GitHub Actions validates Python, Lambda artifacts, and Terraform formatting/configuration on pushes and pull requests. It does not deploy. EKS/observability manifests and a least-privilege GitHub OIDC deployment role remain to be implemented. Never run `terraform destroy`; assess data and security impact before any apply.
