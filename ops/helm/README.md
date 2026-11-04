# Observability release sources

These values and pinned chart archives reproduce the deployed storage configuration.
Do not replace them with the latest chart version during recovery.

| Release | Namespace | Chart | Data claim | Retention |
| --- | --- | --- | --- | --- |
| prometheus | observability | kube-prometheus-stack 92.17.0 | 10 GiB Prometheus, 5 GiB Grafana, 2 GiB Alertmanager | Metrics 24h / 4GB; Alertmanager 120h |
| tempo | observability | tempo 3.2.1 | 10 GiB | Traces 24h |
| loki | loki | loki 20.2.1 | 10 GiB | Logs 24h |

The Prometheus archive was downloaded from the official OCI repository
`oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack:92.17.0`.
Tempo and Loki archives were reconstructed from the chart templates, default
values and files in their installed Helm releases, then rendered and compared
with the installed manifests. No runtime values, release Secrets, passwords or
Terraform state are included in these archives. Archive checksums are recorded
in `charts/SHA256SUMS`.

For an existing, migrated installation:

```bash
helm upgrade prometheus ops/helm/charts/kube-prometheus-stack-92.17.0.tgz \
  -n observability -f ops/helm/values/prometheus.json \
  --skip-crds --no-hooks --server-side=false --wait --timeout 5m
helm upgrade tempo ops/helm/charts/tempo-3.2.1.tgz \
  -n observability -f ops/helm/values/tempo.json \
  --server-side=false --wait --timeout 5m
helm upgrade loki ops/helm/charts/loki-20.2.1.tgz \
  -n loki -f ops/helm/values/loki.json \
  --server-side=false --wait --timeout 5m
```

`--server-side=false` avoids Helm 4 field ownership conflicts with the operator
and maintenance patches. Never use force replacement to resolve those conflicts.
The Grafana deployment uses `Recreate` to avoid simultaneous SQLite writers.
An existing RollingUpdate strategy must have `rollingUpdate` removed when making
that transition. The storage templates use Retain policies.

These commands are **not a migration procedure for an emptyDir installation**.
Read [the recovery runbook](../../docs/observability-recovery.md) before changing
storage. A Helm success alone does not prove adoption: inspect each pod's actual
PVC mount and run readiness and historical query checks.
