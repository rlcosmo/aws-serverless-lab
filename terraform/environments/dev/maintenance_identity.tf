# Bootstrap is performed by the already configured owner identity. Subsequent
# audit/backup calls use a one-hour STS session with this restricted role.
resource "aws_iam_role" "maintenance" {
  name                 = "cosmotech-lab-maintenance"
  max_session_duration = 3600
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/serverless-lab-admin" }
      Action    = "sts:AssumeRole"
    }]
  })
  tags = merge(local.common_tags, { Purpose = "short-lived-audit-and-backup" })
}

resource "aws_iam_role_policy" "maintenance" {
  name = "lab-audit-and-backup"
  role = aws_iam_role.maintenance.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances", "ec2:DescribeVolumes", "ec2:DescribeSnapshots",
          "backup:ListBackupJobs", "backup:ListRestoreJobs", "backup:ListBackupVaults",
          "backup:DescribeBackupJob", "backup:DescribeRestoreJob",
          "cloudwatch:GetMetricStatistics", "cloudwatch:DescribeAlarmHistory", "cloudwatch:DescribeAlarms"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = ["ssm:SendCommand"]
        Resource = [
          aws_ssm_document.logical_backup_schedule.arn,
          aws_ssm_document.kestra_automation.arn,
          "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:instance/${module.itsm_host.instance_id}"
        ]
      },
      {
        Effect   = "Allow"
        Action   = ["ssm:GetCommandInvocation"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["eks:DescribeCluster"]
        Resource = data.aws_eks_cluster.lab.arn
      },
      {
        Effect   = "Allow"
        Action   = ["backup:StartBackupJob", "backup:ListRecoveryPointsByBackupVault"]
        Resource = "arn:aws:backup:${var.aws_region}:${data.aws_caller_identity.current.account_id}:backup-vault:cosmotech-itsm-dev-vault"
      },
      {
        Effect   = "Allow"
        Action   = ["iam:PassRole"]
        Resource = module.itsm_host.backup_role_arn
        Condition = {
          StringEquals = { "iam:PassedToService" = "backup.amazonaws.com" }
        }
      },
      {
        Effect   = "Allow"
        Action   = ["sns:ListSubscriptionsByTopic", "sns:GetTopicAttributes", "sns:GetSubscriptionAttributes"]
        Resource = [aws_sns_topic.alerts.arn, "${aws_sns_topic.alerts.arn}:*"]
      },
      {
        Effect = "Allow"
        Action = ["ssm:GetParameter"]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/cosmotech/itsm/glpi/automation-credentials",
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/cosmotech/itsm/automation/gmud-signing-key"
        ]
      }
    ]
  })
}

resource "aws_eks_access_entry" "maintenance" {
  cluster_name      = data.aws_eks_cluster.lab.name
  principal_arn     = aws_iam_role.maintenance.arn
  type              = "STANDARD"
  kubernetes_groups = ["cosmotech-maintenance-readers"]
  tags              = local.common_tags
}
