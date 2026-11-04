resource "aws_iam_role" "alertmanager" {
  name = "cosmotech-alertmanager-notifications"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "pods.eks.amazonaws.com" }
      Action    = ["sts:AssumeRole", "sts:TagSession"]
      Condition = {
        StringEquals = {
          "aws:RequestTag/kubernetes-namespace"       = "observability"
          "aws:RequestTag/kubernetes-service-account" = "prometheus-kube-prometheus-alertmanager"
        }
      }
    }]
  })
  tags = local.common_tags
}

resource "aws_iam_role_policy" "alertmanager" {
  name = "publish-only-lab-alerts"
  role = aws_iam_role.alertmanager.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["sns:Publish"]
        Resource = aws_sns_topic.alerts.arn
      },
      {
        Effect   = "Allow"
        Action   = ["kms:GenerateDataKey", "kms:Decrypt"]
        Resource = aws_kms_key.alerts.arn
      }
    ]
  })
}

resource "aws_eks_pod_identity_association" "alertmanager" {
  cluster_name    = data.aws_eks_cluster.lab.name
  namespace       = "observability"
  service_account = "prometheus-kube-prometheus-alertmanager"
  role_arn        = aws_iam_role.alertmanager.arn
}
