# Orders processing candidate

The new Python 3.12 container runtime implements API → SQS → worker → simulated payment → atomic inventory reservation → simulated fulfillment → DynamoDB. Payment and fulfillment use deterministic simulation identifiers; no external money movement occurs. This code is tested locally and built as containers, but current live Orders images have not been replaced. Human approval gates remain mandatory.

The worker handles at-least-once delivery. Checkpoints RECEIVED, PAID, RESERVED and COMPLETED/REJECTED permit bounded retry without double stock reservation. Inventory and order reservation update atomically; duplicate SKUs are aggregated. Insufficient stock rejects and marks the simulated refund. Transient failures remain on SQS for retry and eventual DLQ. Legacy EKS order_id keys and messages remain supported; the Lambda complete mode is opt-in and its current intake behavior is preserved.

The isolated LAB inventory catalog was added to the existing EKS table only after verifying the key was absent. Terraform ignores later item updates so it does not replenish consumed stock. No existing table was replaced. EKS PITR/TTL remain a separate backlog item; business records are retained without an automatic deletion policy.

W3C traceparent/tracestate propagate through the producer, SQS and processing spans. Credentials, Authorization and raw exception text are excluded. Unit tests prove one trace across five spans. A separate live synthetic SDK → OTel collector → Tempo test returned trace `651fd2a1632113141720d79c74263ec8`; this does not prove the still-pending live business deployment.

## Preserved DLQ investigation

At 2026-11-04 10:21:51 UTC the original serverless DLQ contained one message. Message ID `e6f6f394-791d-4d25-a65b-c6f95d757776`, SHA-256 `6a2adea77c8242118880bc811647bc6afee2de1b98112083aa6a40e02bec231e`, previous approximate receive count 6. Its sole top-level field was `invalid`; current validation rejects it with “Unsupported event type or version”. Receiving for investigation used visibility timeout zero; count remained one afterward. No delete or redrive was issued. Receiving itself can increase ApproximateReceiveCount. Original payload is held privately, not published.

Replaying the unmodified invalid payload would fail again. Before any approved replay, establish the intended schema/order ID and compare existing idempotency/order state. Do not delete the original or assume that correcting a payload is duplication-safe.

## Validation

The 74-test suite includes input validation, duplicate delivery, payment failure, stock contention, resumed reservation, fulfillment retry, SQS redrive using Moto, legacy container contracts and safe tracing. Moto business-flow coverage is distinct from a live AWS API/SQS deployment test. Dockerfiles run as UID 10001 and pin the Python base image digest. Baseline Kubernetes manifests are under `ops/kubernetes/orders/`; the protected workflow patches image and selected environment variables rather than recreating infrastructure.

IAM actions were checked against the official AWS service authorization reference and worker GetItem/UpdateItem permissions simulated; DeleteItem remained denied. IAM Policy Autopilot was not installed or run because tool installation is restricted. Optional future reproduction, after tool authorization: `uvx iam-policy-autopilot@latest generate-policies src/orders/consumer/processing.py src/orders/runtime/worker.py --region us-east-1 --account 414053644145 --service-hints dynamodb sqs --pretty`.
