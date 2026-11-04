# Dedicated management plane. The application EKS cluster is never its host.
resource "aws_iam_role" "argocd_host" {
  name = "cosmotech-argocd-dev-host"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow", Action = "sts:AssumeRole",
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
  tags = local.common_tags
}
resource "aws_iam_role_policy_attachment" "argocd_ssm" {
  role       = aws_iam_role.argocd_host.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_secretsmanager_secret" "argocd" {
  for_each                = toset(["admin", "github-deploy-key"])
  name                    = "cosmotech/argocd/${each.key}"
  recovery_window_in_days = 30
  tags                    = local.common_tags
}
resource "aws_iam_role_policy" "argocd_host" {
  role = aws_iam_role.argocd_host.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["eks:DescribeCluster"], Resource = data.aws_eks_cluster.lab.arn },
      { Effect = "Allow", Action = ["secretsmanager:GetSecretValue", "secretsmanager:PutSecretValue"],
      Resource = [for secret in aws_secretsmanager_secret.argocd : secret.arn] }
    ]
  })
}
resource "aws_iam_instance_profile" "argocd" {
  name = "cosmotech-argocd-dev"
  role = aws_iam_role.argocd_host.name
  tags = local.common_tags
}
resource "aws_security_group" "argocd" {
  name        = "cosmotech-argocd-dev"
  description = "Dedicated private Argo CD host. SSM administration only."
  vpc_id      = data.aws_vpc.eks_lab.id
  tags        = local.common_tags
}
resource "aws_vpc_security_group_ingress_rule" "argocd_alb" {
  security_group_id            = aws_security_group.argocd.id
  referenced_security_group_id = data.aws_security_group.observability_alb.id
  from_port                    = 30080
  to_port                      = 30080
  ip_protocol                  = "tcp"
  description                  = "Only the shared TLS ALB reaches Argo CD."
}
resource "aws_vpc_security_group_egress_rule" "argocd_https" {
  security_group_id = aws_security_group.argocd.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}
resource "aws_vpc_security_group_egress_rule" "argocd_dns" {
  for_each          = toset(["tcp", "udp"])
  security_group_id = aws_security_group.argocd.id
  cidr_ipv4         = data.aws_vpc.eks_lab.cidr_block
  from_port         = 53
  to_port           = 53
  ip_protocol       = each.key
}
resource "aws_vpc_security_group_ingress_rule" "argocd_to_eks" {
  security_group_id            = data.aws_eks_cluster.lab.vpc_config[0].cluster_security_group_id
  referenced_security_group_id = aws_security_group.argocd.id
  from_port                    = 443
  to_port                      = 443
  ip_protocol                  = "tcp"
}
resource "aws_instance" "argocd" {
  ami                         = data.aws_ssm_parameter.ubuntu_2404_amd64.value
  instance_type               = "t3.large"
  subnet_id                   = data.aws_subnet.private_a.id
  associate_public_ip_address = false
  vpc_security_group_ids      = [aws_security_group.argocd.id]
  iam_instance_profile        = aws_iam_instance_profile.argocd.name
  monitoring                  = true
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 40
    encrypted             = true
    delete_on_termination = false
  }
  user_data = "#!/bin/bash\nset -eu\nsystemctl enable --now snap.amazon-ssm-agent.amazon-ssm-agent.service\n"
  tags      = merge(local.common_tags, { Name = "cosmotech-argocd-dev", System = "argocd-management" })
  lifecycle { prevent_destroy = true }
}
resource "aws_eks_access_entry" "argocd" {
  cluster_name      = data.aws_eks_cluster.lab.name
  principal_arn     = aws_iam_role.argocd_host.arn
  kubernetes_groups = ["cosmotech-argocd-orders"]
  type              = "STANDARD"
  tags              = local.common_tags
}
resource "aws_lb_target_group" "argocd" {
  name                 = "cosmotech-argocd-dev"
  port                 = 30080
  protocol             = "HTTP"
  target_type          = "instance"
  vpc_id               = data.aws_vpc.eks_lab.id
  deregistration_delay = 30
  health_check {
    path    = "/healthz"
    matcher = "200"
  }
  tags = local.common_tags
}
resource "aws_lb_target_group_attachment" "argocd" {
  target_group_arn = aws_lb_target_group.argocd.arn
  target_id        = aws_instance.argocd.id
  port             = 30080
}
resource "aws_lb_listener_rule" "argocd" {
  listener_arn = data.aws_lb_listener.observability_https.arn
  priority     = 110
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.argocd.arn
  }
  condition {
    host_header { values = ["argocd.cosmotechsolutions.com.br"] }
  }
  tags = local.common_tags
}
resource "aws_backup_selection" "argocd" {
  name         = "cosmotech-argocd-management"
  plan_id      = module.itsm_host.backup_plan_id
  iam_role_arn = module.itsm_host.backup_role_arn
  resources    = [aws_instance.argocd.arn]
}
resource "aws_cloudwatch_metric_alarm" "argocd_status" {
  alarm_name          = "cosmotech-argocd-instance-status"
  namespace           = "AWS/EC2"
  metric_name         = "StatusCheckFailed"
  dimensions          = { InstanceId = aws_instance.argocd.id }
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 2
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "missing"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  tags                = local.common_tags
}
output "argocd_instance_id" { value = aws_instance.argocd.id }

# Fixed bootstrap payload contains code/config only; all credentials are generated
# on the private host and stored directly in Secrets Manager.
resource "aws_ssm_document" "argocd_bootstrap" {
  name          = "CosmoTech-Install-Dedicated-ArgoCD"
  document_type = "Command"
  content = jsonencode({
    schemaVersion = "2.2"
    description   = "Install pinned dedicated K3s and Argo CD without modifying the application EKS cluster"
    mainSteps = [{
      action = "aws:runShellScript"
      name   = "installArgoCD"
      inputs = {
        timeoutSeconds = "1800"
        runCommand = concat(["#!/bin/bash", "set -Eeuo pipefail", "umask 077", "install -d -m 0700 /opt/cosmotech/argocd-source"],
          [for name in fileset("${path.module}/../../../ops/argocd", "*") :
          "printf '%s' '${base64encode(file("${path.module}/../../../ops/argocd/${name}"))}' | base64 --decode > '/opt/cosmotech/argocd-source/${name}'"],
        ["bash /opt/cosmotech/argocd-source/install.sh"])
      }
    }]
  })
  tags = local.common_tags
}
