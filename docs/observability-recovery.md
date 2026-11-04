# Observability storage and recovery

## Migration performed on 2026-11-04

Prometheus, Grafana, Alertmanager and Loki originally stored data in emptyDir.
Tempo stored `/var/tempo` in its container filesystem. Charts and user values
were captured privately before any controller changes. Container image versions
were preserved throughout the migration.

Source sizes were approximately 565 MiB Prometheus, 54 MiB Grafana, 44 MiB Tempo
and 7 MiB Loki. Five encrypted gp3 volumes, totaling 37 GiB, were provisioned via
the existing CSI driver and `gp3-encrypted-retain` StorageClass. PVC declarations
are in `ops/kubernetes/observability-pvcs.yaml` and Helm sources in `ops/helm/`.

Temporary privileged helper pods mounted the source nodes read-only. Each writer
was briefly suspended during capture, with an independent 20-second resume
watchdog and an exit trap. These are **crash-consistent captures**, not claims of
an application-native online snapshot. WAL recovery was tested. Archives were
copied outside the repository to a mode-700 directory, with mode-600 archives
and SHA-256 digests. No archive contents are published in Git.

Before replacing the original pods:

- Grafana's recovered SQLite database passed `PRAGMA integrity_check`: `ok`.
- An isolated Prometheus instance replayed its WAL, became ready, and returned
  37 historical `up` series using `count(max_over_time(up[24h]))`.
- Isolated Tempo and Loki instances started with recovered data and became ready.
  Validation gossip/ring settings isolated them from the live instances.
- AWS Backup jobs were started for both source node disks; both completed.

After validation, staging copies were refreshed from the original writers before
cutover. The operators were paused while immutable StatefulSet claim templates
were changed; controllers were recreated with orphan propagation. The original
pods needed explicit replacement because StatefulSet adoption attempted an
immutable pod volume update. The operators were unpaused. Only after recovery
validation were the original pods replaced. The resulting pods' actual PVC
mounts were inspected, and another restart exercised persistence.

Do not infer zero RPO or uninterrupted collection from these tests. Suspension,
controller reconciliation and restarts introduce collection gaps. Historical
data recovery is proven; a transaction-level, zero-loss telemetry migration is
not claimed.

## Backup policy

Terraform discovers each CSI volume by its PVC and cluster tags and assigns all
five to the existing daily AWS Backup plan. Backups are retained for 14 days.
The scheduled snapshot RPO target is up to 24 hours plus backup job duration;
snapshot retention does not extend application data retention beyond 24 hours.
Re-plan after replacing a PVC so the backup selection follows its new volume.

AWS Backup snapshots of running services are crash-consistent. Before a recovery
exercise, preserve current data and use a new EBS volume; never restore over an
original. The dedicated AWS Backup restore role is service-assumable and is not
an interactive administrator role. Backup vault and volume encryption remain on.

Recovery sequence:

1. Identify a COMPLETED recovery point and capture its creation time.
2. Obtain its restore metadata and start an EBS restore into an isolated volume
   in the required AZ, encrypted and using gp3.
3. Wait for the restore job to complete. Bind the new volume to a separate PV/PVC
   with `Retain`, using the existing filesystem; do not format it.
4. Mount restored data in a validation pod with no live Service selectors and no
   live gossip membership. Check SQLite integrity, Prometheus WAL and historical
   samples, Loki queries and Tempo queries as applicable.
5. Record restore job IDs, start/finish times, observed recovery-point age,
   integrity findings, resource IDs and temporary cost. A completed AWS job alone
   is not application integrity validation.
6. Stop validation compute after testing. Preserve originals and evidence.

## Rollback

Retain all original AWS Backup recovery points, private capture archives and PVCs.
Never roll Helm back to the old emptyDir values: that would hide the durable data.
Recover a backup into a separate claim and validate it, then repoint a reviewed
release configuration. Keep the same application version until recovery succeeds.
Restoring old data can discard newer telemetry; record the selected RPO explicitly.

Private migration evidence is under `/tmp/cosmotech-continuation-20261104/`.
This is a working copy, not the long-term backup system; durable EBS recovery
points are held in `cosmotech-itsm-dev-vault`.

## Cost

37 GiB at the reference gp3 rate of USD 0.08/GiB-month is about USD 2.96/month,
excluding snapshot storage, temporary restored volumes, tax and credits.
The alerting KMS key adds a reference USD 1/month plus requests. An additional
37 GiB isolated restoration temporarily adds the same USD 2.96/month equivalent,
prorated while retained. See [EBS pricing](https://aws.amazon.com/ebs/pricing/).

## Completed isolated recovery results

All five initial EBS restore jobs completed into distinct volumes in `cosmotech-recovery`. The CSI v2 attach policy initially denied the restored volumes because they lacked `ebs.csi.aws.com/cluster=true`; adding that cluster ownership tag to the restored copies corrected attachment without expanding IAM permissions. Static PVs/PVCs use Retain.

- Grafana SQLite integrity: ok, one user and four data sources.
- Prometheus: WAL replay Ready, 42 historical up series.
- Loki: four labels and an actual historical query returning one stream/line.
- Alertmanager: Ready, empty captured state recovered.
- Initial Tempo crash snapshot: Ready but malformed block metadata and no historical results. This failed semantic validation and is retained for analysis.
- A second Tempo capture used graceful scale-to-zero, waited until the snapshot cut existed, and resumed the same original PVC. Backup `6bfeae38-3662-4e29-b73e-cc7c2061375f`, snapshot `snap-0da8501e7373d8447`, restore `78ccf942-4af4-4f8f-844e-be30d35c3d0a`, recovered volume `vol-048aa25041c575363`: clean block polling, 38 blocks, 20 historical traces returned. Observed local write quiescence about 37 seconds; AWS timestamps and local wall clock differ, so no precise cross-clock RTO is claimed.

Application validation took about 17 minutes across the initial restore exercise, including the attachment-tag correction; this is not a guaranteed per-volume recovery SLO. Daily snapshot RPO is up to 24 hours plus job duration. The Tempo retry snapshot age was about four minutes when the isolated restore was requested (local clock).

The reusable `scripts/backup_tempo_consistently.py` requires an assumed-role session, validates the encrypted CSI volume, bounds the maintenance wait and resumes Tempo in finally. It records monotonic quiescence/readiness timings. The ordinary daily snapshot plan remains crash-consistent; schedule an authorized quiesced capture when application-consistent Tempo recovery is required.

Validation pods were removed; originals and six restored volumes totaling 47 GiB were retained. Additional restored-disk cost is USD 3.76/month equivalent at USD 0.08/GiB-month, prorated while kept. This supersedes the earlier five-copy estimate.

## ITSM recovery

`ops/itsm/backup-and-restore-test.sh` creates protected logical dumps and reconstruction configuration, then restores MariaDB and PostgreSQL into newly named containers with no network and no published ports. The second exercise, 10:32:58–10:33:26 UTC (28 seconds), recovered 447 GLPI tables including the test ticket and GMUD, 25 PostgreSQL public tables and zero MariaDB check errors. Test containers were stopped and volumes retained. Source dumps are point-in-time captures; the measured restore interval is not the scheduled-backup RPO. GLPI/MariaDB restart separately took 18 seconds with the test records preserved.

An initial fresh EC2 backup completed. A final EC2 backup was requested after the updated dumps; check the latest execution report for completion. No original EC2 host, database or disk was overwritten. An entire restored EC2 boot/SSM exercise was not performed; EBS restore, database integrity and reconstruction archives were tested separately.
