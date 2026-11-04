# CosmoTech AWS Lab — Execution Status

Updated: 2026-11-04 00:47 UTC

## Scope and preservation

- Main repository: `/opt/aws-serverless-lab`, branch `main`, remote `origin` is `https://github.com/rlcosmo/aws-serverless-lab.git`.
- Independent MCP directory `cosmotech-infrastructure-mcp/` is pre-existing, untracked in this repository, and has not been inspected, modified, or staged.
- No destructive Terraform action, data deletion, queue redrive, Git reset/clean/stash, or forced push was performed. Only temporary, newly-created Kubernetes routing objects from the failed external-endpoint experiment were removed. The pre-existing serverless DLQ message remains untouched.
- Git `main` has pending, validated public-access documentation and Terraform changes. The independent untracked MCP directory remains unstaged.
- The earlier $100/month cap is removed by the current instruction. Cost checks and the existing $100 AWS Budget alert remain in place; the alert does not cap spending.

## Initial live audit

- AWS identity: `arn:aws:iam::414053644145:user/serverless-lab-admin`; region `us-east-1`.
- EKS `aws-eks-istio-lab-dev`: ACTIVE, Kubernetes 1.37; three Spot `c7i-flex.large` nodes Ready. Public API CIDR is restricted to the administrator `/32`.
- One VPC (`10.20.0.0/16`), two public and two private subnets, one available NAT Gateway, existing public observability ALB, and private ITSM `t3.large` EC2 (`i-0def4e806c49cf60e`, `10.20.11.150`) with encrypted 50 GiB gp3 root volume.
- Prometheus, Grafana, Loki, Tempo, and OTel pods were ready. Observability data paths use `emptyDir`; there is no EBS CSI driver or PVC migration yet.
- Active serverless API uses API Gateway IAM authorization, Lambda, SQS, and DynamoDB. SQS source queues were empty; EKS DLQ empty; a pre-existing serverless DLQ message remains untouched. Serverless DynamoDB PITR and TTL are enabled; EKS table PITR/TTL are not.
- Legacy `orders` namespace has two unhealthy deployments with empty queue/table configuration. They remain untouched pending source-of-truth confirmation. Healthy active deployments are in `orders-api` and `orders-worker`.
- Cluster Autoscaler is running but logs denied reads for `storage.k8s.io/volumeattachments` and `resource.k8s.io` resources; investigate version/RBAC before changing it.

## Public GLPI and Kestra — implemented and verified

- DNS provider is Cloudflare (`bjorn.ns.cloudflare.com`, `robin.ns.cloudflare.com`). Both required CNAMEs already existed and target `k8s-observability-633f55bc55-702046070.us-east-1.elb.amazonaws.com`; no DNS changes or Cloudflare API credentials were needed.
- Reused the existing internet-facing ALB and ACM wildcard `*.cosmotechsolutions.com.br` (issued, current expiry May 19, 2027). No second ALB or certificate was created.
- Added AWS WAF `cosmotech-public-ingress`, associated with the ALB. Default action blocks; public allow is restricted to GLPI and Kestra hostnames; other existing dashboard hosts are allowed only from the EKS administrator CIDR; ITSM requests are rate-limited to 1,200 per source IP per five minutes. Current capacity: 21 WCU.
- WAF logs are sent to CloudWatch log group `aws-waf-logs-cosmotech-public-ingress`, retention 30 days. Authorization, Cookie, and query strings are redacted; sampled requests are disabled. 71 events were present during initial smoke checks.
- ALB inbound 80/443 is Internet-wide only behind the active WAF. EC2 inbound TCP/8088 is allowed only from the ALB security group. No database or Docker application ports are public.
- Installed Nginx on the private EC2 through SSM. It proxies to GLPI `127.0.0.1:8080` and Kestra `127.0.0.1:8081`; both Docker host bindings remain loopback-only. MariaDB and PostgreSQL remain internal Docker services without host port mappings. Nginx access logs omit query strings.
- Kestra canonical URL is `https://kestra.cosmotechsolutions.com.br/`. GLPI uses its login page; Kestra Basic Auth is enabled.
- Terraform directly manages a private-IP target group, healthy EC2 target `10.20.11.150:8088`, `/healthz` probe, and HTTPS listener rule priority 100 for the two hostnames. The AWS Load Balancer Controller did not register the external EC2 target through a selectorless Service/EndpointSlice; only those temporary objects were removed. No application or data resources were changed.
- Validation from the current network: both DNS CNAMEs resolve to the ALB; `curl`/`openssl` certificate verification passed for both; HTTP returned 301 to HTTPS; GLPI returned HTTP 200; Kestra UI returned a login redirect; unauthenticated Kestra API returned HTTP 401; target health reports `healthy`; Grafana remains accessible from the configured administrator network.
- A separate non-administrator vantage was unavailable, so a public-source WAF denial test for Grafana remains unverified. WAF rules and the current administrator `/32` were read back from AWS.
- AWS WAF published pricing gives a baseline of `$5/month` per ACL and `$1/month` per rule, plus request charges. Current design estimate is `$8/month` base for one ACL and three customer rules, plus request/log usage. Reusing the ALB avoided a new load balancer charge. [AWS WAF pricing](https://aws.amazon.com/waf/pricing/).
- More complete billing baseline before this phase: Cost Explorer `$9.52` for Nov 1–3 (excluding credits/refunds), subject to billing delay. Published hourly estimates at 730 hours were EKS control plane `$73.00`, one NAT `$32.85`, and on-demand `t3.large` `$60.96`, totaling `$166.80` before Spot compute, EBS, ALB, LCU, data, CloudWatch, Backup, tax, and credits. [EKS](https://aws.amazon.com/eks/pricing/), [VPC](https://aws.amazon.com/vpc/pricing/), [EC2 T3](https://aws.amazon.com/ec2/instance-types/t3/).

## Code and validation

- `terraform fmt -check -recursive`: passed.
- `terraform validate`: passed.
- Terraform DEV state contains 58 resources; latest refreshed plan reports no changes. Public routing apply added 3 resources, 0 changed, 0 destroyed; WAF phase added 6 resources and later updated logging redaction in place.
- `kubectl apply --dry-run=server` passed for the original ingress manifests; temporary failed Service/EndpointSlice/Endpoints/Ingress objects were removed. Existing observability ingress remains declaratively restricted by WAF and CIDR policy.
- Python unit suite: 43 passed. Ruff: passed. `compileall`: passed. Shell syntax check: passed. `git diff --check`: passed after direct target-group and documentation changes.
- Staged-file secret scan passed for the first public-access commit; no secrets, credentials, or runtime files were staged. Rerun after the current changes.
- Commit `5045b68 feat(itsm): publish GLPI and Kestra through protected ALB` was pushed to `origin/main`. Direct Terraform listener/target-group routing and final access documentation are validated and ready for a separate commit and push.

## Costs and budgets

- Existing AWS Budget `LAB-SERVERLESS-LIMIT` has a `$100 USD` monthly alert threshold with prior notifications preserved. Current instruction removes the cap; no enforcement change was made.
- Budget API previously reported `$0` while Cost Explorer reported `$9.52`; billing data lag/discrepancy remains open. Cost Explorer forecast API returned `DataUnavailableException` due to limited billing history.
- No fixed cap is being enforced. Review current Cost Explorer and WAF/CloudWatch usage before future provisioning.

## Remaining backlog and human dependencies

- Durable Prometheus, Alertmanager, Loki, and Tempo storage; EBS CSI install and safe storage migration/restore test.
- Cluster Autoscaler authorization/version correction, based on compatible least-privilege permissions.
- Alert destination is not configured/verified; do not invent a recipient or send alerts without a real endpoint.
- GLPI login is reachable, but UI login, ticket/GMUD creation, workflow, and backup restore exercise remain unverified.
- Kestra authentication is active, but workflows and GLPI integration are not implemented. Real approver identities for DEV, QA, PO/PM, and Infra/SRE are unavailable; approvals must not be simulated and no GMUD-gated deploy may proceed without them.
- EKS Orders manifests/source are not tracked in this repo; payment, inventory, fulfillment, end-to-end SQS retry/DLQ/idempotency tests and complete trace propagation remain incomplete.
- Existing ECR OIDC trust is for a separate GitHub repo, not this repository. Current GitHub Actions validates code only; no deploy workflow or approval gates are ready.
- Cloudflare DNS was already correct. If records must change later, Cloudflare admin access is a human dependency because no DNS API credentials are available.

## Next steps

1. Stage only reviewed main-repository paths, rerun the staged secret scan, commit, and push without force.
2. Record the new commit hash here in a follow-up continuity update if needed.
3. Continue with durable observability and safe recovery plan, then resolve human dependencies for real approval-gated ITSM workflows.

## Rollback notes

- Public route rollback: first restore ALB inbound 80/443 to the administrator `/32`; verify dashboard access; then remove the Terraform listener rule/target group and EC2 ALB ingress in a reviewed plan. Keep the shared ALB, ACM certificate, WAF, EC2, and application data.
- Never delete Docker volumes, databases, state, or the existing serverless DLQ message during access rollback.
- Backups from before this phase are under `/tmp/cosmo-public-access-backup-20261104/`; the state backup is private and must only be used for state-corruption recovery.
