locals {
  observability_claims = {
    prometheus   = "prometheus-prometheus-kube-prometheus-prometheus-db-prometheus-prometheus-kube-prometheus-prometheus-0"
    grafana      = "grafana-data"
    alertmanager = "alertmanager-prometheus-kube-prometheus-alertmanager-db-alertmanager-prometheus-kube-prometheus-alertmanager-0"
    tempo        = "storage-tempo-0"
    loki         = "storage-loki-0"
  }
}

# Kubernetes owns volume lifecycle. Terraform discovers volumes; it never creates
# or deletes these application disks. Re-plan after any PVC replacement.
data "aws_ebs_volume" "observability" {
  for_each = local.observability_claims
  filter {
    name   = "tag:kubernetes.io/created-for/pvc/name"
    values = [each.value]
  }
  filter {
    name   = "tag:kubernetes.io/cluster/aws-eks-istio-lab-dev"
    values = ["owned"]
  }
}

resource "aws_backup_selection" "observability" {
  name         = "cosmotech-observability-volumes"
  plan_id      = module.itsm_host.backup_plan_id
  iam_role_arn = module.itsm_host.backup_role_arn
  resources    = [for volume in data.aws_ebs_volume.observability : volume.arn]
}

resource "aws_iam_role" "restore_testing" {
  name = "cosmotech-lab-restore-testing"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "backup.amazonaws.com" }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.current.account_id }
        ArnLike      = { "aws:SourceArn" = "arn:aws:backup:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*" }
      }
    }]
  })
  tags = merge(local.common_tags, { Purpose = "isolated-restore-testing" })
}

resource "aws_iam_role_policy_attachment" "restore_testing" {
  role       = aws_iam_role.restore_testing.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
}
