# CosmoTech AWS Lab — Execution Status

Updated: 2026-11-04 19:13 UTC

## Current — approval-free DEV CI/CD pilot, 2026-11-04

**Owner instruction:** “neste primeiro momento vamos testar ci/cd sem necessidade de nenhuma aprovação”. This explicitly supersedes the earlier approval/GMUD hold for the Orders API DEV pilot only. No human approval was fabricated; the DEV policy says approval_required=false. Billing, private repository visibility, AWS permissions, WAF and application authentication were not changed.

- **Delivered:** GitHub Actions → immutable ECR artifact → scoped GitHub App → automatic GitOps PR merge → dedicated Argo CD → EKS. Original CI `41875936763` was reused; no unnecessary rebuild or full Python suite. Targeted automatic promotion run [41893014782](https://github.com/rlcosmo/cosmotech-orders-api/actions/runs/41893014782) SUCCESS. An initial promotion attempt exposed shallow Git history; fetch-depth=0 corrected only that cause.
- **Scope/control:** API variable DEV_AUTO_PROMOTE=true; GitOps gitops/environments/dev/release-policy.json permits only an image-field change for orders-api-dev / namespace orders-api, checked against the successful CI SHA/digest. The App token remains scoped to GitOps. SHA-matched merge has no admin override. Argo owns EKS Deployment writes; Actions never patches it directly. GitOps automated validation run `41892515886` passed without reviewer jobs.
- **PRs:** #1 MERGED by rlcosmo-cosmotech-gitops[bot], image promotion commit `be3b7bf1f7f9fd9e18aa2e2a1b72a8b6df3edcbd`; previous policy-fix PR #2 CLOSED without merge because the owner changed this DEV requirement. Branch/history retained. No fake QA/PO/Infra approval records or paid protections.
- **Argo:** Synced / Healthy, conditions empty, last deployment operation Succeeded at promotion revision be3b7bf. Application/AppProject configuration was applied only to namespace argocd on the dedicated management K3s (SSM `1f222010-d08a-4c1a-aead-49a64a699c97`). Automatic sync and self-heal enabled, pruning disabled. Post-rollout validation SSM `76a80f01-67e2-4eb5-9e5d-205b93597dcd` SUCCESS; public authentication/API 401 and GitHub/EKS connectivity remain healthy.
- **EKS release:** Deployment generation 11 rolled out successfully. Pod orders-api-54c9f6dfdb-zlc48, 2/2 Running, zero restarts. Image tag sha-106b861dae142628ec0ff5960b65fa4c2e95c563; actual container imageID equals `sha256:9a45e770876979144754ead545772a7c7225a2e281b6f09eceeda165e441a9e0`. Other workloads were not deployed.
- **Smoke passed:** GET /health/live 200; GET /health/ready 200; GET /version 200 (2.0.0-lab); GET random nonexistent order 404 (exercises storage read); invalid POST /orders {} 400. No valid order was submitted. Evidence /tmp/cosmotech-dev-cicd-smoke.json; reusable script is in canonical API scripts/smoke_dev_release.py. Local-only port-forward was stopped. Full business/SQS processing is outside this deployment smoke scope.
- **Versioned changes:** GitOps 1332b46 (DEV policy/validation/auto-sync), be3b7bf (App promotion), 8652768 (mode/rollback documentation); API 845cc94 (auto-merge), 09a3f9a (fetch ancestry), 1c497e2 (smoke script/docs). SHA image still derives from the tested application source 106b861; later API commits changed pipeline/tests/docs only. No new AWS resources or recurring infrastructure charges.
- **Pause/rollback:** set DEV_AUTO_PROMOTE=false; disable auto_promote in the GitOps DEV policy and automated.enabled in the Application, then apply the current management manifests on K3s. Roll back application versions through GitOps to a known validated immutable image; no direct kubectl rollout undo or destructive force/prune. Mandatory approvals are a later governance decision, not a requirement silently removed from unrelated environments.

**Result:** this first DEV CI/CD test is complete under the owner's new no-approval scope. The earlier governance/restore checkpoints below remain historical evidence; they no longer block this pilot. Future application source pushes use the normal test/build/scan/OIDC publish/automatic DEV promotion path.

## Historical pending-work validation — 2026-11-04

This checkpoint supersedes the historical continuation sections below. CD is **not complete**: no approved release, authorized merge, Argo sync or new EKS version rollout has occurred.

- **App validated:** ID was stored as a repository Secret, rather than Variable; workflow now supports both without exposing values or replacing the key. Targeted runs [41885072665](https://github.com/rlcosmo/cosmotech-orders-api/actions/runs/41885072665) and [41885793878](https://github.com/rlcosmo/cosmotech-orders-api/actions/runs/41885793878) SUCCESS. They reused the approved image artifact; build/test/scan/publish jobs were skipped. Token explicitly requested only GitOps Contents/Pull requests write + Metadata read; runtime test found exactly one accessible repository and denied access to private infrastructure. Authentication errors stop before checkout/write; no PAT fallback.
- **Image CI remains approved:** original run `41875936763` SUCCESS; ECR repository IMMUTABLE, tag `sha-106b861dae142628ec0ff5960b65fa4c2e95c563`, digest `sha256:9a45e770876979144754ead545772a7c7225a2e281b6f09eceeda165e441a9e0`. No new image build was required. IaC run `41876857339` is now SUCCESS too; two legacy Lambda ZIP changes were never applied.
- **GitOps PR [#1](https://github.com/rlcosmo/cosmotech-gitops/pull/1):** OPEN, author `app/rlcosmo-cosmotech-gitops`, head `95ef119a65825ea38fc3b076caa1c9f5792eba5c`; one deployment image-field change only, including SHA tag and pinned digest. Kubernetes server dry-run passed. No approved reviews. verify-protections failed and native approval jobs were skipped; main remains unprotected. No merge or deployment.
- **Guard fix PR [#2](https://github.com/rlcosmo/cosmotech-gitops/pull/2):** OPEN, branch `fix/fail-closed-release-check`, commit `553ac14`. The final release check must run even when upstream jobs skip/fail and reject any non-success result. Actual negative test: verify-protections FAILURE, four stages SKIPPED, terminal release-approved FAILURE. Not merged; GitOps main still uses the previous guard. A failed workflow is not technical merge protection while main is unprotected.
- **Governance block:** private branch protection and rulesets return 403; owner type User; dev Environment exists without reviewer rules. PR reviews/checks are not technically mandatory in the current plan. Four-stage private native Environment reviewers require Enterprise, not Pro/Team. The existing public index has the four native reviewer environments. Options A/B/C with costs, trust boundaries and implementation requirements are in [the existing setup guide](github-app-setup.md). No billing, visibility, organization transfer or approval-mechanism change was made. Owner must choose/authorize a solution before release.
- **Argo/EKS:** authenticated public API and GitHub/EKS connectivity pass; `orders-api-dev` Healthy/OutOfSync, conditions empty, desired main revision `418af25df4b5ae43b0d0e4f7dd77fc963c3e07b5`. Main has not changed: the unmerged PR image is correctly not the desired main release. EKS still runs `otel-20261103-014209`. Auto-sync remains disabled; this is not equivalent to approval enforcement.
- **Admin secret located:** `arn:aws:secretsmanager:us-east-1:414053644145:secret:cosmotech/argocd/admin-hLO0zy`, name `cosmotech/argocd/admin`, region us-east-1, active, JSON username admin/password present. GetSecretValue succeeded as `arn:aws:iam::414053644145:user/serverless-lab-admin`; no AccessDenied or password reset. No value was printed. Console path: select account 414053644145 → US East (N. Virginia)/us-east-1 → Secrets Manager → Secrets → search exact name → open secret → Retrieve secret value → JSON password field. Use this navigation rather than the failed deep link.
- **Grafana:** login HTTP 200, `/api/health` database ok. Owner explicitly answered “validado” to admin login, dashboard and datasource-query checks. Password was never retrieved or reset. Container is shell-less, so no diagnostic tool was installed and no service changed.
- **Automation restore:** SSM `92706722-5919-449e-8c07-a52f9c143262` SUCCESS. Dump capture `20261104T160813Z` restored into a distinct PostgreSQL container/volume, network none, zero published ports. SHA256 passed; restored 25 public tables, 11 flow records, 2 executions, 21 logs. Test container stopped; live DB untouched. Root-only evidence `/opt/cosmotech/backups/restore-tests/automation-20261104T182026Z/evidence.json`; test volume retained. Scope is database recovery; engine boot and local storage artifacts were not exercised.
- **Argo config restore:** SSM `b2f4a769-c3b5-4db1-b6ce-263210895f41` SUCCESS. Capture `20261104T155928Z` copied/extracted into a new root-only restore directory; checksum/SQLite integrity passed, five config files recovered, Helm/Application/AppProject/repository/cluster records present. Six encrypted Argo Secrets decrypted and format-validated only in memory using the backed-up encryption configuration. No controller started or live data changed; full EC2 boot is not claimed. Evidence under `/opt/cosmotech/backups/argocd/restore-tests/*/evidence.json`. Script lives in canonical IaC `scripts/restore_argocd_config_isolated.py`, outside the bootstrap payload.
- **Tempo restore evidence reused:** existing AWS restore `78ccf942-4af4-4f8f-844e-be30d35c3d0a` is COMPLETED; snapshot `snap-0da8501e7373d8447`, encrypted restored volume `vol-048aa25041c575363`, prior isolated query returned 20 historical traces/38 blocks at 10:39 UTC. See canonical observability `docs/observability-recovery.md` and protected `tempo-consistent-query-evidence.json`. No repeat restore/new EBS volume was necessary. This proves that prior consistent capture; latest timer snapshot `snap-0f1e942f10d61e0ed` has not separately been restored.
- **Scope/cost:** no new AWS resources, paid plan, key rotation, component reinstall or application rollout. Existing-host restoration tests used bounded CPU/memory and retained protected copies; source data/volumes and independent MCP remain untouched. Evidence/backup data/secrets were not published.
- **Published changes:** Orders `8d86312`, `bd2d8c0`; Automation `8cb68d1`; IaC `b2d8c2b`, `03c28ef`; GitOps policy fix `553ac14` only on the unmerged PR #2 branch. Validation: shell/Python/workflow syntax, live App scope/PR creation/idempotency, server dry-run, actual isolated restores and expected negative guard outcome. No full Python suite was repeated.

**Next:** owner selects governance option, enables the corresponding technical controls, records real GLPI/GMUD + DEV/QA/PO-PM/Infra-SRE approvals for the exact PR/head SHA/digest, then authorizes merge. Only after that may Argo sync and EKS version/rollout be validated. No owner approval is inferred from this operational work.

## Finalization — 2026-11-04

- Administrative Argo CD login through public HTTPS revalidated successfully; anonymous API 401, GitHub/EKS connected, pilot Healthy/OutOfSync. Username `admin`; credential remains in Secrets Manager `cosmotech/argocd/admin`, us-east-1. No password was displayed, reset or stored in documentation. The initial EC2 backup is COMPLETED.
- Orders image: `sha-106b861dae142628ec0ff5960b65fa4c2e95c563`; ECR digest `sha256:9a45e770876979144754ead545772a7c7225a2e281b6f09eceeda165e441a9e0`. Published CI artifact matches ECR. Pipeline [41875936763](https://github.com/rlcosmo/cosmotech-orders-api/actions/runs/41875936763) succeeded; no GitOps merge or Argo synchronization was performed.
- The earlier apparent queue resolved into invalid Trivy action version / OIDC subject mismatch failures. These were corrected, then the three missing Terraform read operations were scoped and validated by IAM Access Analyzer with no findings. No administrator policy, static GitHub AWS credentials, new EC2 or duplicate infrastructure was introduced. Source/state ownership stays in the canonical infrastructure repository.
- Current owner dependencies: GitHub App configuration (instructions requested and provided) and private-environment reviewer capability. Owner said the GitHub plan is unchanged. App setup can proceed independently; it cannot approve releases or bypass the missing protections. See [setup guide](github-app-setup.md).
- New published commits: Orders `106b861`; infrastructure `5c17fcf`, `ea55093`. This finalization created no resources and added no recurring resource cost. Terraform changed only OIDC trust subjects and scoped CI read permissions.

## Historical continuation — 2026-11-04 16:12 UTC

This checkpoint is historical; the pending-work validation above is authoritative.

| Area | Completed | Pending / blocked |
|---|---|---|
| Grafana | Exact-host WAF allowance + per-IP limit, HTTPS/login 200, anonymous API 401; other dashboard restrictions retained; password never retrieved or reset | Owner validates current-password login, dashboards and datasource access in browser |
| Backups | Previous Snap systemd/PV RBAC fixes preserved; Tempo job `2313d3cc-9bed-4ed4-9a02-71d5496e0697` COMPLETED; both daily timers active; fresh logical backup command `b980483f-034c-4257-8afc-a62f427912ad` succeeded, including the Automation database; all artifact SHA256 checks passed | Isolated restore of latest Tempo snapshot and full Argo EC2 boot restore remain pending; logical cleanup is manual |
| SSM | CloudTrail denial identified; new maintenance-role session successfully executes only approved fixed documents on the ITSM host | No AdministratorAccess or wildcard shell grant added |
| Kestra Automation | Private independent engine/DB/storage; runner ownership and startup retries fixed; health check active; functional GLPI workflow SUCCESS; logs/auth/restart persistence passed; personal services unchanged | GitHub App owner configuration for cross-repository integration |
| GitHub | Six private component repositories published with original ancestry; original files retained as frozen snapshots; MCP untouched; Worker extraction deferred | IaC retains required first-party bootstrap/Lambda build snapshots until artifact references replace file() dependencies |
| Dedicated Argo host | `i-0b33fdd51332e04e5`, private IP `10.20.11.199`, t3.large, encrypted 40 GiB gp3, no public IP/SSH, IMDSv2, SSM, monitoring/alarm, backup selection; both EC2 checks OK | Initial EC2 backup job `1aca94d0-d3fc-4b5d-bde1-b38b62dc8dd8` is COMPLETED (confirmed in this finalization) |
| K3s / Argo | K3s `v1.37.1+k3s1`, Helm `v4.3.1`, chart `10.12.1`; Ready components, authenticated public HTTPS/API 401; GitHub read-only deploy key; EKS role + namespace RBAC; post-reboot login/GitHub/EKS checks passed; a fresh controller argocd-k8s-auth token was accepted by EKS without exposing/storing it | Pilot `orders-api-dev` is Healthy / OutOfSync, manual sync only; no application deployment performed |
| CD ownership | Argo role limited to orders-api; no Secret access or Worker writes. Legacy GitHub identity can read but no longer patch Orders API; legacy script deploy mode blocked | GitHub rejected private-repository reviewer protections (422) and branch protection readback (403). The new workflow fails closed unless all four real reviewer rules and branch protection are verified; no effective gate protection is claimed |
| CI | Orders run `41875936763` SUCCESS: lint/tests/build/Trivy and OIDC ECR publication. Fixed invalid Trivy action reference and immutable OIDC subjects in both roles; scoped missing plan reads to the VPC, managed EBS CSI policy and lab table. IaC plan command completed with 0 additions / 2 legacy Lambda ZIP updates / 0 destroys; not applied | IaC run `41876857339` still reports in_progress after successful plan/cleanup logs. GitOps proposal skipped because GitHub App is not configured; deployment remains blocked by real approval requirements |

Argo URL: https://argocd.cosmotechsolutions.com.br/ . Admin credential and read-only GitHub key are in Secrets Manager `cosmotech/argocd/admin` and `cosmotech/argocd/github-deploy-key`; values never entered Git, Helm or Terraform. Root-only K3s SQLite/config backup passed integrity/SHA256, daily timer active; daily encrypted EC2 backup reuses the existing vault/plan. No extra ALB, EKS cluster or NAT was created. Bootstrap/rollback/restore details live in the canonical infrastructure README.

Canonical checkouts are under `/home/lab/cosmotech-repositories/`. Only `cosmotech-infrastructure-iac/terraform/environments/dev` now manages the original S3 backend/key; no state migration or duplicate state. Never apply the frozen main-repository Terraform snapshot. Two unrelated legacy Lambda ZIP updates were excluded from reviewed applies and remain for explicit review.

Approximate new baseline: Argo t3.large USD 60.74/month (AWS Pricing API USD 0.0832/hour × 730), 40 GiB gp3 ~USD 3.20, two Secrets ~USD 0.80, Argo WAF rules ~USD 2; Grafana rules add another ~USD 2. Total ~USD 68.74/month incremental before monitoring, snapshots, traffic/logs and taxes. Existing ALB/NAT/EKS costs continue; no spending cap is enforced.

Validation: 77 Python tests and Ruff passed before extraction; targeted bootstrap Ruff and shell syntax passed; Terraform formatting/validation and fresh reviewed non-destructive plans passed; IAM Access Analyzer found no findings in the new read-only CI policy; Kubernetes dry-run and actual authorization checks passed. Published main CI/security runs `41860054555` and `41860053365` succeeded. Orders component workflow `41875936763` is now SUCCESS. IaC validation passed and the plan command completed without errors; final workflow status still reports in_progress. No application deploy occurred.

Next actions: owner follows [GitHub App setup](github-app-setup.md), then retry only Orders publish/proposal jobs using approved artifacts. Confirm final IaC workflow status. Owner has not changed the GitHub plan: required reviewers for private environments are unavailable on Free/Pro/Team; branch protection alone does not solve these gates. Do not change billing or publish private repositories. Keep releases blocked until protections and real GLPI/GMUD approvals are established. Obtain browser-only Grafana confirmation and schedule isolated restore tests; Worker extraction remains deferred.

Published code commits in main: `201dba1`, `c6f02e4`, `6f3e67f`. Component publication commits:
- `cosmotech-infrastructure-iac`: `62a8df2`.
- `cosmotech-kubernetes-rbac`: `c6c2bbb`.
- `cosmotech-gitops`: `b7051c5`.
- `cosmotech-orders-api`: `c5770a2`.
- `cosmotech-observability`: `4e97c6b`.
- `cosmotech-automation`: `41c4215`.
Additional published updates: infrastructure `6791637`, `9d41aa6`; GitOps workflow `05e4214` and fail-closed guard `418af25`; observability `4ad66dd`, `965c55a`; RBAC API write removal `7ab9306`. Documentation/index publication is the final main commit for this continuation.

## Active continuation — 2026-11-04 15:44 UTC

This checkpoint supersedes older status tables and open dependencies below.

- Grafana: WAF previously allowed dashboards only from the EKS administrator CIDR, explaining external 403. Added exact-host Grafana allowance and 1,200 requests/IP/5min limit; other dashboards retain restrictions. Login HTTPS 200, certificate verified, anonymous dashboard API 401. Password unchanged and never retrieved. Current-password login/dashboard/datasource validation needs the owner in a browser; no authenticated success is claimed.
- Backups: existing systemd runs already succeeded at 11:48/11:50 UTC. Prior failures were AWS CLI Snap writing under read-only `/root/snap`, then missing get permission on Tempo's named PV. Existing fixes preserved and versioned. Logical capture SHA256 checks passed; both timers active. Tempo backup `2313d3cc-9bed-4ed4-9a02-71d5496e0697` COMPLETED, encrypted volume `vol-091bf80370bf3410f`, snapshot `snap-0f1e942f10d61e0ed`. No repeat quiescence was necessary. Restore of this latest snapshot remains pending; earlier isolated restore evidence remains valid for its original capture. Logical archives remain root-only on encrypted EBS and are covered by EC2 backup, not a separate S3 object upload. Retention: Tempo 14 days; logical capture cleanup remains manual.
- SSM: CloudTrail identifies maintenance-role SendCommand denials at 11:41/11:49 UTC for the target EC2 and fixed Kestra document. Current scoped policy already includes both. New STS session successfully sent command `d4e44e93-2dac-4521-9959-454d7019475f`; no wildcard shell permission or AdministratorAccess added.
- Kestra Automation: private loopback 8082, independent PostgreSQL/storage/credentials, SSM SecureString. Fixed runner file ownership and transient startup disconnect handling; added engine health check. Execution `5zPbS9yltD4yce0IHarDUH` SUCCESS, GLPI technical integration completed, logs accessible, anonymous API 401, execution persisted after dedicated-engine restart. Personal services unchanged. Existing EC2 has ~3.9 GiB available RAM and 33 GiB free disk; no resize needed.
- Local validation: 77 Python tests, Ruff, Terraform validation/format, shell syntax and diff checks passed. No MCP repository modification. Fresh Terraform plans used; no old plans reused.
- WAF increment: two Grafana rules, approximately USD 2/month plus traffic/logs. No new ALB.
- Next: publish checkpoint, split required repositories incrementally, review fresh dedicated-Argo EC2 plan. Existing four human approval gates still apply to Orders deployment; no approval was simulated.

## Current validated state

This current report supersedes the dated historical checkpoints below. Installed does not imply that every integration has been functionally validated.

| Component | Installed / current evidence | Remaining limitation |
| --- | --- | --- |
| EKS / Istio | Three Ready nodes, current Orders API/worker 1/1; healthy installations preserved | Autoscaler 1.36.1 versus Kubernetes 1.37.1; no upstream 1.37 binary found |
| API Gateway / Lambda / SQS / DynamoDB | Existing IAM-protected intake retained; earlier signed smoke persisted one idempotent order | Complete processing candidate not deployed; one invalid original DLQ message retained |
| Prometheus / Grafana / Loki / Tempo / Alertmanager | Five encrypted Retain PVCs, 37 GiB, historical recovery and second restart validated | Scheduled EBS snapshots remain crash-consistent; Tempo needs quiescence for proven historical recovery |
| OTel | Live synthetic SDK → collector → Tempo trace retrieved | Full live business-flow tracing awaits approved Orders deploy |
| GLPI / MariaDB | Technical OAuth, create/read/update ticket 1 and change 1, restart persistence, isolated restore integrity | Human approvals remain None; no fabricated approval |
| Kestra / PostgreSQL | Existing authenticated deployment preserved, logical DB restore checked | No Enterprise license; no independent technical account or authenticated flow tests |
| DNS / TLS / ALB / Nginx / WAF | GitHub-hosted external test passed; internal ports inaccessible, dashboards denied | Latest external run includes anonymous GLPI API denial |
| Terraform / CI | Formatting and DEV validation pass; 74 tests pass locally | New application artifacts are prepared, not applied through Terraform |

## Completed changes and evidence

- Observability migration inspected actual data/mounts, captured private backups with SHA-256, preserved versions, prepared recovery and verified SQLite/WAL/history before replacing pods. Five live volumes remain encrypted and retained; no original data volume was deleted. Detailed recovery limits and rollback are in [observability-recovery.md](observability-recovery.md).
- Seven initial EBS backup jobs completed (two source node disks plus five application disks). All five initial isolated restores completed. Prometheus returned 42 historical series; Grafana SQLite integrity was ok; Loki returned historical log data; Alertmanager started with captured empty state.
- Initial Tempo restored copy was Ready but had malformed metadata/no history: **failed semantic integrity**. Graceful quiesced backup `6bfeae38-3662-4e29-b73e-cc7c2061375f` and isolated restore `78ccf942-4af4-4f8f-844e-be30d35c3d0a` recovered 20 historical traces and 38 blocks. About 37 seconds local write quiescence; daily RPO up to 24 hours plus job duration. No zero-loss or guaranteed RTO claim. Six retained restored volumes total 47 GiB; validation pods removed.
- MariaDB/PG logical restore test 10:32:58–10:33:26 UTC: 28 seconds, 447 GLPI tables including the test ticket/GMUD, 25 PG public tables, zero MariaDB check errors. GLPI/MariaDB restart took 18 seconds and preserved records. Isolated test containers stopped, volumes retained. An initial fresh EC2 backup completed; final job `fa816a90-2e4f-4cb3-9fde-c2983603461a` completed at 11:34:44 UTC after updated dumps. Whole restored EC2 boot was not tested.
- GLPI technical user `svc-cosmotech-automation` (id 7), isolated entity/profile, OAuth client and minimal ticket/change/document/followup rights created. Approval rights are zero. Credentials stored at SSM SecureString `/cosmotech/itsm/glpi/automation-credentials`, no secrets published. Personal users/passwords unchanged. Test records clearly labeled; no real ticket changed.
- Exactly `orders/orders-api` and `orders/orders-worker` were identified as broken legacy components, specifications archived, and removed under explicit owner authorization. Current workloads in their separate namespaces remain healthy. Services, Secrets, namespaces, tables, queues and application PVCs preserved.
- Encrypted SNS topic, email subscription, CloudWatch ALARM/OK actions and Alertmanager Pod Identity configured. Subscription confirmed. Controlled alert and resolution actions succeeded; two-hour SNS metrics: 15 published, 6 delivered, 0 failed (earlier publishes occurred before confirmation). Prometheus canary now inactive; Alertmanager sends resolved notifications. Owner inbox confirmation remains distinct from provider delivery.
- Four GitHub environments require real reviewer `rlcosmo`, main only, administrator bypass false. Repository-specific OIDC uses immutable repository/owner IDs, ref and environment. IAM scopes ECR, EKS discovery and a fixed private SSM tunnel; Kubernetes denies Secrets and permits only named Orders Deployment updates. See [ITSM gates](itsm-change-gates.md).
- Candidate Orders runtime includes simulated payment, atomic inventory, fulfillment, idempotent checkpoints, retries/DLQ and safe OTel propagation. LAB catalog added only to an absent reserved key, without resetting existing stock; existing tables preserved. Live application images remain unchanged pending real approvals. See [Orders details and DLQ investigation](orders-processing.md).
- GLPI bridge, HMAC metadata validation and disabled Kestra flow are implemented/tested in source. `GMUD_INTEGRATION_READY=false`; no full integration/deploy success is claimed. Owner confirmed no Kestra Enterprise license; no Kestra technical account was created and no personal Basic Auth credential reused. A repository GitHub App is still required.
- External security run [41812329759](https://github.com/rlcosmo/aws-serverless-lab/actions/runs/41812329759) passed from a GitHub-hosted runner outside the administrator network: verified TLS, redirects, GLPI reachability, Kestra API 401, dashboard/unknown host 403 and closed internal/database ports.

## Validation and resources

74 pytest tests passed, Ruff/compileall/pip dependency checks passed, both Lambda ZIP imports passed, Terraform recursive formatting and DEV validation passed, shell syntax and staged secret-pattern checks passed. New Docker images build locally as UID 10001 with a pinned base digest. Business E2E tests use Moto; live collector/Tempo test is a separate synthetic trace, not a deployed order-processing proof.

New/modified resources: five application EBS volumes/PVCs; six retained recovery volumes; backup selection/restore role; SNS/KMS/subscription/canary and alarm actions; Alertmanager role/Pod Identity; GLPI technical user/profile/entity/OAuth and enabled OAuth API; four protected GitHub environments, OIDC role/EKS access/RBAC, fixed SSM document, worker checkpoint policy and LAB catalog item. No new cluster, node, ALB, NAT or ITSM instance was provisioned. Only the two authorized legacy Deployments were removed.

Initial/bootstrap operations used the existing configured IAM user `serverless-lab-admin`; this is recorded rather than retrospectively claiming role-only access. A restricted maintenance role was then provisioned. Final audit/backup calls use a one-hour STS assumed-role session, read-only EKS access except named Tempo scaling, and no Secret read access. GitHub deployment uses OIDC rather than static AWS keys. No IAM user access keys were changed.

## Costs

Additional 37 GiB live gp3 ≈ USD 2.96/month; retained 47 GiB restoration copies ≈ USD 3.76/month; KMS key reference USD 1/month and one standard alarm reference USD 0.10/month: about **USD 7.82/month incremental fixed/reference cost while copies are retained**, plus snapshots, requests, notifications, data, logs, tax/credits. This is not the whole lab bill. Existing EKS/NAT/EC2/ALB charges continue. Sources: [EBS](https://aws.amazon.com/ebs/pricing/), [KMS](https://aws.amazon.com/kms/pricing/), [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/). Existing USD 100 Budget with 50/80/100 percent alerts remains a notification threshold, not a spending cap.

## Open dependencies

1. Independent officially supported Kestra technical authentication without changing personal access; no Enterprise license available. Authenticated workflow creation/execution/results/logs/restart and GLPI integration remain pending.
2. Owner installs a repository-limited GitHub App and stores its private credential securely; complete real bridge tests before enabling integration.
3. Owner supplies four actual GitHub approvals for the probe/deploy. Runtime OIDC/tunnel and new Orders live E2E remain blocked until approval; no simulated approvals.
4. Cluster Autoscaler matching 1.37 binary release; preserve healthy current cluster in the meantime.
5. Schedule application-consistent Tempo capture, review EKS Orders PITR/retention and optionally perform full EC2 boot recovery. Original invalid DLQ message must not be replayed unchanged.
6. Owner confirms actual inbox receipt of alert and recovery. Provider delivery is proven.

## Publications

Published baseline commits: `5b857fb` observability/recovery, `c4d5aca` external security, `84173f9` recoverable Orders/tracing. Subsequent commit/run results are recorded in the final verification section. Independent `cosmotech-infrastructure-mcp/` remains untracked, untouched and excluded from commits. No history rewrite or remote change.

## Final verification — 2026-11-04

- Published `c1b0b61` (`feat(automation): enforce real change gates and scoped oidc deployment`) after `84173f9`. Secret-pattern scans passed and the MCP directory was excluded.
- CI [41822293068](https://github.com/rlcosmo/aws-serverless-lab/actions/runs/41822293068) passed both Python and Terraform jobs for the automation commit. Previous Orders CI [41822002621](https://github.com/rlcosmo/aws-serverless-lab/actions/runs/41822002621) also passed.
- Latest external run [41822310511](https://github.com/rlcosmo/aws-serverless-lab/actions/runs/41822310511) succeeded, including anonymous GLPI OAuth API 401 after API enablement. Evidence is retained as the run artifact.
- Approval probe [41822306059](https://github.com/rlcosmo/aws-serverless-lab/actions/runs/41822306059) passed source/tests/artifacts and read-back protection checks using the runner token. GitHub reports **waiting**, pending environment `dev`, required reviewer `rlcosmo`, zero approvals. No AWS credential/deployment job has begun. Owner must approve all four gates in sequence to test OIDC/private connectivity; this probe never deploys an application even after approval.
- Final EC2 backup COMPLETED. All three nodes Ready; current Orders workloads 1/1; no legacy Deployment remains in `orders`; six recovery PVCs Bound, recovery validation pods absent. Maintenance role can scale only Tempo and cannot patch Orders Deployments or read Secrets.
- Remaining daily logical-dump scheduling, application-consistent Tempo scheduling, full EC2 boot recovery and real Kestra orchestration are **not claimed complete**. Existing AWS Backup schedules cover disks; on-demand logical dumps/restores were verified.

## Historical execution checkpoints (superseded)

## Continuation checkpoint — 2026-11-04

This section supersedes earlier statements about zero PVCs and unknown approvers.
The previous execution record below is retained as historical evidence.

- Revalidated AWS identity, EKS nodes, Helm releases and actual pod volume mounts.
  All three EKS nodes were Ready; healthy components were not reinstalled.
- Migrated Prometheus, Grafana, Alertmanager, Loki and Tempo to five encrypted
  gp3 PVCs totaling 37 GiB, preserving the existing application versions and
  recovered data. Isolated WAL/startup/SQLite checks passed before replacing
  original pods. New pods mount the intended claims. A second restart was run
  to exercise persistence. See `docs/observability-recovery.md` for limits and
  rollback; zero RPO is not claimed.
- All seven on-demand EBS backup jobs (two source node disks and five application
  disks) reached COMPLETED. Five isolated EBS restore jobs have been started;
  restored-data validation is still in progress at this checkpoint. Daily backup
  selection now includes all five observability volumes, with 14-day retention.
- MariaDB and PostgreSQL consistent logical dumps were restored to separate,
  network-isolated Docker containers. The 28-second exercise recovered 447 GLPI
  tables (zero tickets/changes at capture) and 25 Kestra public tables. MariaDB
  table checks reported zero errors. Restored containers were stopped; their
  volumes and protected evidence remain on the ITSM host. This does not yet
  prove functional ticket/workflow recovery. A fresh EC2 backup was requested.
- Removed exactly `orders/orders-api` and `orders/orders-worker` after preserving
  their specifications privately and confirming empty queue/table settings.
  Current deployments in `orders-api` and `orders-worker` remained healthy.
  No namespace, Service, Secret, queue, table or application PVC was removed.
- Created GLPI `svc-cosmotech-automation`, an isolated lab entity, restricted
  profile and OAuth client. OAuth authentication passed. Credentials are in SSM
  SecureString `/cosmotech/itsm/glpi/automation-credentials`; none are published.
  Personal users/passwords were preserved. API functional checks are in progress.
- Provisioned an encrypted SNS alert topic, owner email subscription, CloudWatch
  canary alarm, existing alarm/recovery actions and a dedicated Alertmanager Pod
  Identity role. Email remains PendingConfirmation in AWS at this checkpoint.
  Owner responded to the confirmation request; no delivery is yet claimed.
- Owner designated real GitHub user `rlcosmo` for all four approval gates for now.
  Protected environment configuration and OIDC/deploy work are in progress;
  no human approval has been simulated and no application deploy has occurred.
- Upstream releases were checked again: latest observed Cluster Autoscaler binary
  is 1.36.1; a chart 9.60.0 release is not a 1.37 binary. Keep the compatibility
  gap open. Recent autoscaler logs show normal loops and no forbidden errors.
- Terraform plans for notifications, backup selection/restore role and Alertmanager
  identity were reviewed before apply; they contained additions and alarm action
  updates, without resource destruction or replacement. Formatting and validation
  passed. Incremental publication and remaining checks are in progress.

## Scope and preservation

- Main repository: `/opt/aws-serverless-lab`, branch `main`, remote `origin` is `https://github.com/rlcosmo/aws-serverless-lab.git`.
- Independent MCP directory `cosmotech-infrastructure-mcp/` is pre-existing, untracked in this repository, and has not been inspected, modified, or staged.
- No destructive Terraform action, data deletion, queue redrive, Git reset/clean/stash, or forced push was performed. Only temporary, newly-created Kubernetes routing objects from the failed external-endpoint experiment were removed. The pre-existing serverless DLQ message remains untouched.
- Git `main` matches `origin/main` at `34771d9` before the current EBS CSI changes; the independent untracked MCP directory remains untouched and unstaged.
- The earlier $100/month cap is removed by the current instruction. Cost checks and the existing $100 AWS Budget alert remain in place; the alert does not cap spending.

## Initial live audit

- AWS identity: `arn:aws:iam::414053644145:user/serverless-lab-admin`; region `us-east-1`.
- EKS `aws-eks-istio-lab-dev`: ACTIVE, Kubernetes 1.37; three Spot `c7i-flex.large` nodes Ready. Public API CIDR is restricted to the administrator `/32`.
- One VPC (`10.20.0.0/16`), two public and two private subnets, one available NAT Gateway, existing public observability ALB, and private ITSM `t3.large` EC2 (`i-0def4e806c49cf60e`, `10.20.11.150`) with encrypted 50 GiB gp3 root volume.
- Prometheus, Grafana, Loki, Tempo, and OTel pods were ready. Observability data paths use `emptyDir`; there is no EBS CSI driver or PVC migration yet.
- Active serverless API uses API Gateway IAM authorization, Lambda, SQS, and DynamoDB. SQS source queues were empty; EKS DLQ empty; a pre-existing serverless DLQ message remains untouched. Serverless DynamoDB PITR and TTL are enabled; EKS table PITR/TTL are not.
- Legacy `orders` namespace has two unhealthy deployments with empty queue/table configuration. They remain untouched pending source-of-truth confirmation. Healthy active deployments are in `orders-api` and `orders-worker`.
- Cluster Autoscaler `v1.36.1` is running against Kubernetes `1.37.1`. It previously lacked read access to scheduling resources and status ConfigMap permissions. Added a separately managed read-only ClusterRole for `volumeattachments` and DRA resources, plus a namespaced Role/RoleBinding for status ConfigMap operations. `kubectl auth can-i` checks pass, the status ConfigMap now exists, and its last 20 seconds of logs showed no authorization errors. Version compatibility remains under review; [upstream recommends matching the CA minor to the Kubernetes minor](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/README.md#releases), and no v1.37 CA release was present in the official releases list at the time checked.

## Durable observability storage — foundation enabled

- Added Terraform-managed IAM role, scoped EKS Pod Identity association, AWS-managed `AmazonEBSCSIDriverPolicyV2` attachment, and EKS `aws-ebs-csi-driver` add-on `v1.67.2-eksbuild.1` for Kubernetes 1.37. The trust policy limits role assumption to the `kube-system/ebs-csi-controller-sa` session tags. The EKS Pod Identity agent was already present.
- Add-on reached `ACTIVE` with no reported health issues. Both controller pods became `6/6 Ready`, all three node DaemonSet pods `3/3 Ready`, and all three EKS nodes remained `Ready`.
- Added and applied `ops/kubernetes/storageclass-gp3.yaml` (`gp3`, encryption required, `Retain`, expansion allowed, `WaitForFirstConsumer`). Server-side dry-run passed. There are still zero PVCs and zero CSI-managed EBS volumes, so no storage volume cost has started.
- Prometheus, Alertmanager, Loki, Tempo, and Grafana Helm releases still use ephemeral `emptyDir` data paths. Existing release values are not checked into source control, and chart packages/versions are not all available from configured Helm indexes. Their PVC migration, backup, and restore exercise remain pending to avoid silently discarding active metrics, logs, traces, or Grafana state. No observability release was restarted or upgraded.
- Terraform plan was reviewed at 4 additions, 0 changes, 0 destroys, then applied successfully. The add-on has no separate EKS add-on price; its controller and node agents consume existing EC2 capacity. No EBS volumes were provisioned.

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
- Official Kestra documentation confirms webhook trigger keys are embedded in URL paths and may appear in proxy, load balancer, and access logs. WAF redacts URI paths, Authorization, Cookie, and query strings; Nginx omits paths and queries. No webhook or GLPI API integration was created pending real OAuth credentials and reviewer configuration.
- AWS WAF published pricing gives a baseline of `$5/month` per ACL and `$1/month` per rule, plus request charges. Current design estimate is `$8/month` base for one ACL and three customer rules, plus request/log usage. Reusing the ALB avoided a new load balancer charge. [AWS WAF pricing](https://aws.amazon.com/waf/pricing/).
- More complete billing baseline before this phase: Cost Explorer `$9.52` for Nov 1–3 (excluding credits/refunds), subject to billing delay. Published hourly estimates at 730 hours were EKS control plane `$73.00`, one NAT `$32.85`, and on-demand `t3.large` `$60.96`, totaling `$166.80` before Spot compute, EBS, ALB, LCU, data, CloudWatch, Backup, tax, and credits. [EKS](https://aws.amazon.com/eks/pricing/), [VPC](https://aws.amazon.com/vpc/pricing/), [EC2 T3](https://aws.amazon.com/ec2/instance-types/t3/).

## Code and validation

- `terraform fmt -check -recursive`: passed.
- `terraform validate`: passed.
- Terraform DEV state previously contained 58 resources; current state includes the four EBS CSI resources listed below. Public routing apply added 3 resources, 0 changed, 0 destroyed; WAF phase added 6 resources and logging redactions were updated in place.
- The EBS CSI foundation Terraform apply added 4 resources, 0 changed, 0 destroyed; latest state includes the role, policy attachment, Pod Identity association, and add-on. StorageClass server-side dry-run and apply passed.
- GitHub Actions `validate` runs for `34771d9` (`41751849803`) and `dbfd751` (`41806774501`) completed successfully. GitHub reports zero deployment environments.
- `kubectl apply --dry-run=server` passed for the original ingress manifests; temporary failed Service/EndpointSlice/Endpoints/Ingress objects were removed. Existing observability ingress remains declaratively restricted by WAF and CIDR policy.
- Added `ops/kubernetes/cluster-autoscaler-observability-rbac.yaml`; Kubernetes server-side dry run and apply passed. Verified the service account can read scheduling APIs and get/update the named status ConfigMap. The Autoscaler status ConfigMap was created and no authorization errors appeared in the final 20-second log window. Existing node count remains 3; all were Ready.
- Python unit suite: 43 passed. Ruff: passed. `compileall`: passed. Shell syntax check: passed. `git diff --check`: passed after direct target-group and documentation changes.
- Staged-file secret scans passed for public-access and log-hardening commits; no secrets, credentials, or runtime files were published. The MCP directory remains untracked and unstaged.
- Commits pushed to `origin/main`: `5045b68 feat(itsm): publish GLPI and Kestra through protected ALB`, `6af9abf feat(itsm): route public domains to private EC2 target`, `0382b40 docs: record public ITSM access implementation`, `ba3d88b fix(security): keep webhook keys out of access logs`, `6bd573d docs: record ITSM approval gates and blockers`, `34771d9 fix(autoscaler): complete cluster autoscaler rbac permissions`, and `dbfd751 feat(observability): enable encrypted gp3 storage driver`.

## Costs and budgets

- Existing AWS Budget `LAB-SERVERLESS-LIMIT` has a `$100 USD` monthly alert threshold with prior notifications preserved. Current instruction removes the cap; no enforcement change was made.
- Budget API previously reported `$0` while Cost Explorer reported `$9.52`; billing data lag/discrepancy remains open. Cost Explorer forecast API returned `DataUnavailableException` due to limited billing history.
- No fixed cap is being enforced. Review current Cost Explorer and WAF/CloudWatch usage before future provisioning.

## Remaining backlog and human dependencies

- Migrate Prometheus, Alertmanager, Loki, Tempo, and Grafana to appropriately sized PVCs using `gp3-encrypted-retain`; establish backup, retention, and a restore test before declaring persistence complete. Existing PVC count is zero; do not restart or upgrade the releases until active emptyDir data and exact chart values are handled.
- Cluster Autoscaler is still `v1.36.1` on Kubernetes `1.37.1`. Authorization errors for observed DRA/storage APIs and status ConfigMap were corrected additively. Recheck official releases and update to a Kubernetes 1.37-matched image when published; validate in a staged manner.
- Alert destination is not configured/verified; do not invent a recipient or send alerts without a real endpoint.
- GLPI login is reachable, but UI login, ticket/GMUD creation, workflow, and backup restore exercise remain unverified.
- Kestra authentication is active, but workflows and GLPI integration are not implemented. Real approver identities for DEV, QA, PO/PM, and Infra/SRE are unavailable; approvals must not be simulated and no GMUD-gated deploy may proceed without them.
- GitHub REST API reports zero deployment environments. GLPI OAuth client/service account, Kestra API/webhook secret, and a repository-scoped AWS OIDC role are not configured; these are prerequisites for the requested end-to-end change workflow.
- EKS Orders manifests/source are not tracked in this repo; payment, inventory, fulfillment, end-to-end SQS retry/DLQ/idempotency tests and complete trace propagation remain incomplete.
- Existing ECR OIDC trust is for a separate GitHub repo, not this repository. Current GitHub Actions validates code only; no deploy workflow or approval gates are ready.
- Cloudflare DNS was already correct. If records must change later, Cloudflare admin access is a human dependency because no DNS API credentials are available.

## Next steps

1. Continue durable observability storage by capturing active ephemeral data safely, identifying/pinning exact chart artifacts and values, sizing PVCs, and running backup/restore tests before Helm release updates.
2. Track Cluster Autoscaler release compatibility; update from v1.36.1 to the supported Kubernetes 1.37 minor once available, with rollback and readiness checks.
3. Resolve real approver identities and an alert receiver before implementing approval-gated ITSM workflows or notification delivery.
4. Configure a GLPI OAuth service account/client, protected GitHub Environments, Kestra API/webhook secret, and repository-scoped AWS OIDC role before building the live workflow.
5. Track EKS Orders source/manifests and tests for retries, DLQ, idempotency, payment/inventory/fulfillment, and trace propagation.

## Rollback notes

- Public route rollback: first restore ALB inbound 80/443 to the administrator `/32`; verify dashboard access; then remove the Terraform listener rule/target group and EC2 ALB ingress in a reviewed plan. Keep the shared ALB, ACM certificate, WAF, EC2, and application data.
- Never delete Docker volumes, databases, state, or the existing serverless DLQ message during access rollback.
- Backups from before this phase are under `/tmp/cosmo-public-access-backup-20261104/`; the state backup is private and must only be used for state-corruption recovery.
