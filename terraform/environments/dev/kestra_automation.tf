locals {
  kestra_automation_files = {
    "Dockerfile.runner"                = file("${path.module}/../../../ops/itsm/kestra-automation/Dockerfile.runner")
    "functional-flow.yaml"             = file("${path.module}/../../../ops/itsm/kestra-automation/functional-flow.yaml")
    "validate_kestra_automation.py"    = file("${path.module}/../../../scripts/validate_kestra_automation.py")
    "requirements-automation.txt"      = file("${path.module}/../../../requirements-automation.txt")
    "scripts/test_kestra_glpi.py"      = file("${path.module}/../../../scripts/test_kestra_glpi.py")
    "src/automation/__init__.py"       = file("${path.module}/../../../src/automation/__init__.py")
    "src/automation/bridge.py"         = file("${path.module}/../../../src/automation/bridge.py")
    "src/automation/change_control.py" = file("${path.module}/../../../src/automation/change_control.py")

    "docker-compose.yml" = file("${path.module}/../../../ops/itsm/kestra-automation/docker-compose.yml")
    "application.yaml"   = file("${path.module}/../../../ops/itsm/kestra-automation/application.yaml")
    "install.sh"         = file("${path.module}/../../../ops/itsm/kestra-automation/install.sh")
  }
}
resource "aws_ssm_document" "kestra_automation" {
  name          = "CosmoTech-Install-Private-Kestra-Automation"
  document_type = "Command"
  content = jsonencode({
    schemaVersion = "2.2"
    description   = "Install the owner-authorized isolated OSS engine on loopback 8082; never modify the personal engine"
    mainSteps = [{
      action = "aws:runShellScript"
      name   = "installPrivateAutomation"
      inputs = {
        timeoutSeconds = "600"
        runCommand = concat(["#!/bin/bash", "set -Eeuo pipefail", "umask 077", "install -d -m 0700 /opt/cosmotech/automation-source/scripts /opt/cosmotech/automation-source/src/automation"],
          [for name, content in local.kestra_automation_files : "printf '%s' '${base64encode(content)}' | base64 --decode > '/opt/cosmotech/automation-source/${name}'"],
        ["bash /opt/cosmotech/automation-source/install.sh"])
      }
    }]
  })
  tags = merge(local.common_tags, { Purpose = "private-technical-workflows" })
}
resource "aws_iam_role_policy" "itsm_automation_parameters" {
  name = "cosmotech-automation-parameter-read"
  role = "cosmotech-itsm-dev-instance-role"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["ssm:GetParameter"]
      Resource = [
        "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/cosmotech/itsm/glpi/automation-credentials",
        "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/cosmotech/itsm/github/automation-app",
        "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/cosmotech/itsm/automation/gmud-signing-key"
      ]
    }]
  })
}
