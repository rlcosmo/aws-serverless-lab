# CosmoTech AWS Lab — Execution Status

Updated: 2026-11-04 00:58 UTC

## Scope and preservation

- Main repository: `/opt/aws-serverless-lab`, branch `main`, remote `origin` is `https://github.com/rlcosmo/aws-serverless-lab.git`.
- Independent MCP directory `cosmotech-infrastructure-mcp/` is pre-existing, untracked in this repository, and has not been inspected, modified, or staged.
- No destructive Terraform action, data deletion, queue redrive, Git reset/clean/stash, or forced push was performed. Only temporary, newly-created Kubernetes routing objects from the failed external-endpoint experiment were removed. The pre-existing serverless DLQ message remains untouched.
- Git `main` matches `origin/main` at `ba3d88b` before the current change-gate documentation update; the independent untracked MCP directory remains untouched and unstaged.
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
- WAF logs are sent to CloudWatch log group `aws-waf-logs-cosmotech-public-ingress`, retention 30 days. Authorization, Cookie, URI path, and query strings are redacted; sampled requests are disabled. 71 events were present during initial smoke checks.
- ALB inbound 80/443 is Internet-wide only behind the active WAF. EC2 inbound TCP/8088 is allowed only from the ALB security group. No database or Docker application ports are public.
- Installed Nginx on the private EC2 through SSM. It proxies to GLPI `127.0.0.1:8080` and Kestra `127.0.0.1:8081`; both Docker host bindings remain loopback-only. MariaDB and PostgreSQL remain internal Docker services without host port mappings. Updated Nginx config is deployed; an SSM smoke test confirmed URL path and query markers are absent from new access-log lines. No Kestra webhook existed before this hardening.
- Kestra canonical URL is `https://kestra.cosmotechsolutions.com.br/`. GLPI uses its login page; Kestra Basic Auth is enabled.
- Terraform directly manages a private-IP target group, healthy EC2 target `10.20.11.150:8088`, `/healthz` probe, and HTTPS listener rule priority 100 for the two hostnames. The AWS Load Balancer Controller did not register the external EC2 target through a selectorless Service/EndpointSlice; only those temporary objects were removed. No application or data resources were changed.
- Validation from the current network: both DNS CNAMEs resolve to the ALB; `curl`/`openssl` certificate verification passed for both; HTTP returned 301 to HTTPS; GLPI returned HTTP 200; Kestra UI returned a login redirect; unauthenticated Kestra API returned HTTP 401; target health reports `healthy`; Grafana remains accessible from the configured administrator network.
- A separate non-administrator vantage was unavailable, so a public-source WAF denial test for Grafana remains unverified. WAF rules and the current administrator `/32` were read back from AWS.
- Official Kestra documentation confirms webhook trigger keys are embedded in URL paths and may appear in proxy, load balancer, and access logs. WAF now redacts URI paths, Authorization, Cookie, and query strings; Nginx omits paths and queries. No webhook or GLPI API integration was created pending real OAuth credentials and reviewer configuration.
- Official Kestra documentation confirms webhook trigger keys are embedded in URL paths and can appear in proxy, load balancer, and access logs. No Kestra webhook or GLPI API integration was created until access logs omit paths. The WAF path redaction is applied; the EC2 Nginx config change remains to deploy.
- AWS WAF published pricing gives a baseline of `$5/month` per ACL and `$1/month` per rule, plus request charges. Current design estimate is `$8/month` base for one ACL and three customer rules, plus request/log usage. Reusing the ALB avoided a new load balancer charge. [AWS WAF pricing](https://aws.amazon.com/waf/pricing/).
- More complete billing baseline before this phase: Cost Explorer `$9.52` for Nov 1–3 (excluding credits/refunds), subject to billing delay. Published hourly estimates at 730 hours were EKS control plane `$73.00`, one NAT `$32.85`, and on-demand `t3.large` `$60.96`, totaling `$166.80` before Spot compute, EBS, ALB, LCU, data, CloudWatch, Backup, tax, and credits. [EKS](https://aws.amazon.com/eks/pricing/), [VPC](https://aws.amazon.com/vpc/pricing/), [EC2 T3](https://aws.amazon.com/ec2/instance-types/t3/).

## Code and validation

- `terraform fmt -check -recursive`: passed.
- `terraform validate`: passed.
- Terraform DEV state contains 58 resources; latest refreshed plan reports no changes. Public routing apply added 3 resources, 0 changed, 0 destroyed; WAF phase added 6 resources and logging redactions were updated in place.
- GitHub Actions `validate` run for `ba3d88b` completed successfully (`41750266580`). GitHub reports zero deployment environments.
- `kubectl apply --dry-run=server` passed for the original ingress manifests; temporary failed Service/EndpointSlice/Endpoints/Ingress objects were removed. Existing observability ingress remains declaratively restricted by WAF and CIDR policy.
- Python unit suite: 43 passed. Ruff: passed. `compileall`: passed. Shell syntax check: passed. `git diff --check`: passed after direct target-group and documentation changes.
- Staged-file secret scans passed for public-access and log-hardening commits; no secrets, credentials, or runtime files were published. Current documentation changes need a final check and commit.
- Commits pushed to `origin/main`: `5045b68 feat(itsm): publish GLPI and Kestra through protected ALB`, `6af9abf feat(itsm): route public domains to private EC2 target`, `0382b40 docs: record public ITSM access implementation`, and `ba3d88b fix(security): keep webhook keys out of access logs`.

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
- GitHub REST API reports zero deployment environments. GLPI OAuth client/service account, Kestra API/webhook secret, and a repository-scoped AWS OIDC role are not configured; these are prerequisites for the requested end-to-end change workflow.
- EKS Orders manifests/source are not tracked in this repo; payment, inventory, fulfillment, end-to-end SQS retry/DLQ/idempotency tests and complete trace propagation remain incomplete.
- Existing ECR OIDC trust is for a separate GitHub repo, not this repository. Current GitHub Actions validates code only; no deploy workflow or approval gates are ready.
- Cloudflare DNS was already correct. If records must change later, Cloudflare admin access is a human dependency because no DNS API credentials are available.

## Next steps

1. Continue with durable observability and safe recovery plan.
2. Investigate Cluster Autoscaler compatibility and denied API reads before changing RBAC or upgrading.
3. Resolve real approver identities and an alert receiver before implementing approval-gated ITSM workflows or notification delivery.
4. Configure a GLPI OAuth service account/client, protected GitHub Environments, Kestra API/webhook secret, and repository-scoped AWS OIDC role before building the live workflow.
5. Track EKS Orders source/manifests and tests for retries, DLQ, idempotency, payment/inventory/fulfillment, and trace propagation.

## Rollback notes

- Public route rollback: first restore ALB inbound 80/443 to the administrator `/32`; verify dashboard access; then remove the Terraform listener rule/target group and EC2 ALB ingress in a reviewed plan. Keep the shared ALB, ACM certificate, WAF, EC2, and application data.
- Never delete Docker volumes, databases, state, or the existing serverless DLQ message during access rollback.
- Backups from before this phase are under `/tmp/cosmo-public-access-backup-20261104/`; the state backup is private and must only be used for state-corruption recovery.
