# CosmoTech AWS Lab — Execution Status

Updated: 2026-11-04 00:35 UTC

## Scope and safety

- Main repository: `/opt/aws-serverless-lab`, branch `main`.
- Latest pushed commit at start of this phase: `4c502bc` (`docs: record live lab status and remaining blockers`). Local `main` matches `origin/main`.
- Existing untracked directory `cosmotech-infrastructure-mcp/` is an independent project and remains untouched and unstaged.
- Current instruction removes the previous fixed $100 cap. Costs must still be checked, reported, and monitored; the existing AWS Budgets object is now a $100 monthly alert threshold, not an enforcement limit.
- No destructive operations, Kubernetes mutation, DNS changes, or existing application data changes have been made in this phase. Terraform applied only new public-access protection resources and one private security-group rule; no existing resources were removed or replaced.
- The pre-existing serverless DLQ message remains unread and untouched.

## State and inventory

- AWS identity: `arn:aws:iam::414053644145:user/serverless-lab-admin`, region `us-east-1`.
- Git: `main` clean except for the pre-existing untracked MCP directory; remote `origin` is the main repository and is synchronized.
- Terraform DEV state contains 46 resources; refreshed plan reports no changes.
- EKS `aws-eks-istio-lab-dev` is ACTIVE on Kubernetes 1.37; public and private API endpoints are enabled, with public CIDR restricted to `45.6.218.165/32`.
- Managed Spot node group `aws-eks-istio-lab-dev-spot-named`: 3 `c7i-flex.large` nodes Ready, desired 3/max 3, no reported node-group issues.
- AWS inventory shows one VPC (`10.20.0.0/16`), two public and two private subnets, one available NAT Gateway, three Spot workers, and one private `t3.large` ITSM EC2. The ITSM host has no public IP and an encrypted 50 GiB gp3 volume.
- SQS source queues are empty. EKS DLQ is empty. Serverless DLQ has one visible pre-existing message; do not inspect, redrive, or delete it without a separate approved procedure.
- Orders DynamoDB serverless table is ACTIVE, TTL enabled on `expires_at`, point-in-time recovery enabled according to AWS CLI (the inventory MCP omits PITR details). The separate EKS Orders table has no TTL and no PITR.
- Lambda `aws-serverless-lab-dev-orders-producer` and `...-consumer` are ACTIVE, Python 3.12. API Gateway `POST /orders` uses AWS_IAM.
- Helm releases Alloy, AWS Load Balancer Controller, Kyverno, Loki, OTel Collector, Prometheus stack, and Tempo are deployed. Prometheus, Grafana, Loki, Tempo, and OTel pods are currently ready.
- Two legacy deployments in namespace `orders` remain unhealthy: API `0/1`, Worker `0/1`/Error. Their ConfigMap has empty SQS queue and DynamoDB table values; do not activate them until their ownership and intended queue/table are confirmed. Healthy workloads remain in `orders-api` and `orders-worker` namespaces.
- Prometheus, Alertmanager, Loki, and Tempo use `emptyDir` for their data paths; no PVCs were found. The cluster has only a `gp2` StorageClass, backed by the deprecated in-tree AWS EBS provisioner; EBS CSI driver/add-on is not installed.
- Cluster Autoscaler logs repeatedly show denied reads for `storage.k8s.io/volumeattachments` and `resource.k8s.io` ResourceSlices/DeviceClasses/ResourceClaims. It is running, but compatibility/RBAC impact needs investigation before changing permissions or upgrading it.

## Costs and budgets

- Cost Explorer, 2026-11-01 through 2026-11-03, credits/refunds excluded: `$9.52` (EKS `$4.20`, EC2 Other `$2.48`, EC2 Compute `$1.83`, ELB `$0.65`, VPC `$0.35`; other listed services currently `$0.00`). Data is month-to-date and still subject to billing delay.
- The one AWS Budget, `LAB-SERVERLESS-LIMIT`, was updated to `$100 USD` monthly; three existing alert thresholds were preserved. Budgets do not stop spending. Budget `CalculatedSpend` reported `$0` even while Cost Explorer reported `$9.52`; investigate this reporting lag/discrepancy.
- Cost Explorer forecast API returned `DataUnavailableException` because there is not enough billing history. Current published hourly baselines (730 hours/month) estimate EKS control plane `$73.00`, NAT Gateway `$32.85`, and existing `t3.large` compute `$60.96`; combined baseline `$166.80`, excluding Spot workers, EBS, load balancers, LCU, data, CloudWatch, Backup, taxes, and credits. Pricing sources: [EKS](https://aws.amazon.com/eks/pricing/), [VPC](https://aws.amazon.com/vpc/pricing/), [T3](https://aws.amazon.com/ec2/instance-types/t3/).
- No resource creation is blocked by the removed $100 cap, but future resources still require a cost estimate and purpose review.

## Public GLPI/Kestra access — current phase

- Public DNS NS lookup identifies Cloudflare (`bjorn.ns.cloudflare.com`, `robin.ns.cloudflare.com`). No Cloudflare API credentials or DNS connector are available.
- Both `glpi.cosmotechsolutions.com.br` and `kestra.cosmotechsolutions.com.br` already have CNAMEs to the internet-facing observability ALB `k8s-observability-633f55bc55-702046070.us-east-1.elb.amazonaws.com`; no DNS record update is currently needed if that ALB can safely be reused.
- ACM wildcard `*.cosmotechsolutions.com.br` is ISSUED, DNS validated, and attached to the existing ALB; expiry is 2027-05-19. ALB has HTTP→HTTPS redirect and HTTPS host rules for Grafana, Prometheus, Alertmanager, and Tempo. Unmatched hosts return 404.
- The existing ALB SG restricts HTTP/HTTPS to administrator CIDR `45.6.218.165/32`; `curl` to GLPI/Kestra domains from that allowed source validates TLS but receives 404 because no host routes exist.
- Created and associated regional WAF `cosmotech-public-ingress` with the existing ALB. Default action blocks. It permits only the two ITSM hostnames publicly, permits existing observability routes only from the current administrator `/32`, and rate-limits ITSM hosts at 1,200 requests per source IP per five minutes. Current capacity is 21 WCU.
- WAF logs go to CloudWatch Logs with 30-day retention. Authorization, Cookie, and query-string fields are redacted; request sampling is disabled. WAF access logging is enabled.
- Added a dedicated EC2 security-group rule allowing TCP/8088 from the ALB security group only. No application, MariaDB, or PostgreSQL ports are open to the Internet.
- WAF association was verified with `get-web-acl-for-resource`; Grafana still returns its expected login redirect from the administrator network. GLPI still returns ALB 404 until its target and host route are installed.
- Terraform created six resources (WAF, IP set, log group/configuration, ALB association, and ALB-to-EC2 rule) and updated WAF logging redaction in place. Plans contain no deletes or replacements.
- No dedicated ALB was added. AWS WAF pricing lists a `$5/month` ACL, `$1/month` per customer rule, plus request charges; this design estimates `$8/month` base for one ACL and three rules plus request/log usage (regional pricing and actual usage apply). [AWS WAF pricing](https://aws.amazon.com/waf/pricing/).
- Added versioned Nginx reverse-proxy configuration and installer. It listens on port 8088, proxies to existing loopback-only ports 8080/8081, logs URI without query string, and configures Kestra's canonical HTTPS URL. EC2 proxy install and public route are not active yet.
- Added Kubernetes Service/EndpointSlice/Ingress manifests for private EC2 address `10.20.11.150:8088` and a declarative source manifest for the existing observability Ingress, ready to widen ALB CIDRs only after WAF was active.
- Pre-change backups are stored outside Git at `/tmp/cosmo-public-access-backup-20261104/` (Terraform state backup is mode-restricted). No DNS tokens or service passwords were written there.
- Next steps: publish reviewed source changes; install and test Nginx on EC2 through SSM; apply endpoint/ingress manifests; verify target health, external HTTPS and HTTP redirect, log flow, login behavior, and admin dashboard restrictions.

## Completed previously

- API Gateway IAM authorization, observability ingress restriction, versioned/encrypted Terraform S3 state backend, private SSM-only GLPI/Kestra host, and CI validation workflow.
- Serverless Orders v2 events, idempotent DynamoDB order persistence, scoped IAM, SQS 1 MiB limit, and DynamoDB PITR.
- Signed live API smoke test posted one synthetic order twice and confirmed one `RECEIVED` record plus a `COMPLETE` idempotency claim.
- GLPI/MariaDB and Kestra/PostgreSQL containers are healthy; Kestra authenticated API test returned 200; generated credentials are in SSM SecureString. Do not place credentials in this file.
- Commits: `84081dd` Orders persistence; `4c502bc` live status/backlog.

## Open work

- Public GLPI/Kestra host routing, Nginx reverse proxy install, and external HTTPS tests remain pending.
- Durable observability storage/retention/restore; EBS CSI and storage class setup require tracked manifests and data migration plan.
- Functional alert receiver is missing; receiver identity/endpoint must be supplied or discovered from approved configuration. Do not invent or message a recipient.
- GLPI UI login/ticket/GMUD setup and backup restore exercise remain unverified.
- Kestra flows, GLPI integration, approval-gated GitHub Actions, and deploy workflow are not implemented. Do not fake DEV/QA/PO/PM/Infra/SRE approval identities and do not deploy without real approvals.
- EKS Orders deployment code/manifests are not tracked in this repository. Payment, inventory, fulfillment, full trace propagation, and EKS source-of-truth remain incomplete.
- Existing ECR OIDC role trusts the separate `rlcosmo/aws-eks-istio-lab` repository, not this repository.
- Verify IAM/security-group/NACL/ACM/backup posture in depth; preserve existing resources and data.

## Rollback / continuation

- Public ingress work is staged: (1) WAF is attached and admin access was verified, (2) prepare and test proxy, (3) add target route and widen ALB inbound while WAF remains active, (4) validate public domains. Roll back by restoring the saved Ingress annotations; do not remove the existing ALB or TLS certificate.
- Restore the pre-change Terraform state only for state corruption recovery, never as a routine rollback. Terraform-managed application resources must use forward plans with no destroys/replacements unless explicitly reviewed.
- Continue from the `Public GLPI/Kestra access` section; inspect current state before every mutation because cloud state can change independently.
