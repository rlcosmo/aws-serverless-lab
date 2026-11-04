# The maintenance role may execute only this fixed installer on the existing
# private ITSM host. No caller-controlled command or secret is accepted.
locals {
  logical_backup_files = {
    "publish-backup-status.sh"               = file("${path.module}/../../../ops/itsm/publish-backup-status.sh")
    "run-tempo-backup.sh"                    = file("${path.module}/../../../ops/itsm/run-tempo-backup.sh")
    "backup_tempo_consistently.py"           = file("${path.module}/../../../scripts/backup_tempo_consistently.py")
    "systemd/cosmotech-tempo-backup.service" = file("${path.module}/../../../ops/itsm/systemd/cosmotech-tempo-backup.service")
    "systemd/cosmotech-tempo-backup.timer"   = file("${path.module}/../../../ops/itsm/systemd/cosmotech-tempo-backup.timer")

    "backup-logical.sh"                        = file("${path.module}/../../../ops/itsm/backup-logical.sh")
    "install-backup-schedule.sh"               = file("${path.module}/../../../ops/itsm/install-backup-schedule.sh")
    "systemd/cosmotech-logical-backup.service" = file("${path.module}/../../../ops/itsm/systemd/cosmotech-logical-backup.service")
    "systemd/cosmotech-logical-backup.timer"   = file("${path.module}/../../../ops/itsm/systemd/cosmotech-logical-backup.timer")
  }
}

resource "aws_ssm_document" "logical_backup_schedule" {
  name          = "CosmoTech-Install-Logical-Backup-Schedule"
  document_type = "Command"
  content = jsonencode({
    schemaVersion = "2.2"
    description   = "Install fixed consistent database dumps and a daily UTC timer; preserve existing data and identities"
    mainSteps = [{
      action = "aws:runShellScript"
      name   = "installLogicalBackup"
      inputs = {
        timeoutSeconds = "1000"
        runCommand = concat([
          "#!/bin/bash",
          "set -Eeuo pipefail",
          "umask 077",
          "install -d -m 0700 /opt/cosmotech/backup-source/systemd"
          ], [for name, content in local.logical_backup_files :
          "printf '%s' '${base64encode(content)}' | base64 --decode > '/opt/cosmotech/backup-source/${name}'"
          ], [
          "bash /opt/cosmotech/backup-source/install-backup-schedule.sh || { journalctl -u cosmotech-tempo-backup.service -n 40 --no-pager; exit 1; }"
        ])
      }
    }]
  })
  tags = merge(local.common_tags, { Purpose = "consistent-logical-backup-scheduling" })
}

resource "aws_iam_role_policy" "itsm_consistent_tempo_backup" {
  name = "cosmotech-consistent-tempo-backup"
  role = "cosmotech-itsm-dev-instance-role"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Action    = ["cloudwatch:PutMetricData"]
        Resource  = "*"
        Condition = { StringEquals = { "cloudwatch:namespace" = "CosmoTech/Backups" } }
      },
      {
        Effect   = "Allow"
        Action   = ["backup:StartBackupJob"]
        Resource = "arn:aws:backup:${var.aws_region}:${data.aws_caller_identity.current.account_id}:backup-vault:cosmotech-itsm-dev-vault"
      },
      {
        Effect    = "Allow"
        Action    = ["iam:PassRole"]
        Resource  = module.itsm_host.backup_role_arn
        Condition = { StringEquals = { "iam:PassedToService" = "backup.amazonaws.com" } }
      }
    ]
  })
}

resource "aws_cloudwatch_metric_alarm" "consistent_backup_failure" {
  for_each            = toset(["Logical", "Tempo"])
  alarm_name          = "cosmotech-${lower(each.key)}-backup-failure"
  alarm_description   = "Consistent backup service failed; ignore absent metrics and resolve only after a reported successful run. Inspect the root-only backup evidence and journal."
  namespace           = "CosmoTech/Backups"
  metric_name         = "JobFailure"
  dimensions          = { JobName = each.key }
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "ignore"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  tags                = local.common_tags
}
