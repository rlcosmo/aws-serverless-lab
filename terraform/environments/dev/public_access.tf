data "aws_security_group" "observability_alb" {
  filter {
    name   = "group-name"
    values = ["k8s-observability-6c81249268"]
  }

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.eks_lab.id]
  }
}

data "aws_lb" "observability" {
  name = "k8s-observability-633f55bc55"
}

resource "aws_vpc_security_group_ingress_rule" "itsm_from_observability_alb" {
  security_group_id            = module.itsm_host.security_group_id
  referenced_security_group_id = data.aws_security_group.observability_alb.id
  description                  = "Allow the existing public ALB to reach the private ITSM reverse proxy."
  from_port                    = 8088
  to_port                      = 8088
  ip_protocol                  = "tcp"
}

resource "aws_wafv2_ip_set" "observability_admin" {
  name               = "cosmotech-observability-admin"
  description        = "Administrator source address for existing observability dashboards."
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = data.aws_eks_cluster.lab.vpc_config[0].public_access_cidrs
  tags               = merge(local.common_tags, { System = "public-ingress" })
}

resource "aws_wafv2_web_acl" "public_ingress" {
  name        = "cosmotech-public-ingress"
  description = "Expose GLPI and Kestra only. Restrict observability dashboards to the admin CIDR."
  scope       = "REGIONAL"

  default_action {
    block {}
  }

  rule {
    name     = "rate-limit-public-itsm"
    priority = 0

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 1200
        aggregate_key_type = "IP"

        scope_down_statement {
          or_statement {
            statement {
              byte_match_statement {
                search_string         = "glpi.cosmotechsolutions.com.br"
                positional_constraint = "EXACTLY"
                field_to_match {
                  single_header {
                    name = "host"
                  }
                }
                text_transformation {
                  priority = 0
                  type     = "LOWERCASE"
                }
              }
            }
            statement {
              byte_match_statement {
                search_string         = "kestra.cosmotechsolutions.com.br"
                positional_constraint = "EXACTLY"
                field_to_match {
                  single_header {
                    name = "host"
                  }
                }
                text_transformation {
                  priority = 0
                  type     = "LOWERCASE"
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "cosmotech-public-itsm-rate-limit"
      sampled_requests_enabled   = false
    }
  }

  rule {
    name     = "allow-public-itsm-hostnames"
    priority = 1

    action {
      allow {}
    }

    statement {
      or_statement {
        statement {
          byte_match_statement {
            search_string         = "glpi.cosmotechsolutions.com.br"
            positional_constraint = "EXACTLY"
            field_to_match {
              single_header {
                name = "host"
              }
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }
        statement {
          byte_match_statement {
            search_string         = "kestra.cosmotechsolutions.com.br"
            positional_constraint = "EXACTLY"
            field_to_match {
              single_header {
                name = "host"
              }
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "cosmotech-public-itsm-hosts"
      sampled_requests_enabled   = false
    }
  }

  rule {
    name     = "allow-admin-observability"
    priority = 2

    action {
      allow {}
    }

    statement {
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.observability_admin.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "cosmotech-admin-observability"
      sampled_requests_enabled   = false
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "cosmotech-public-ingress"
    sampled_requests_enabled   = false
  }

  tags = merge(local.common_tags, { System = "public-ingress" })
}

resource "aws_cloudwatch_log_group" "waf_public_ingress" {
  name              = "aws-waf-logs-cosmotech-public-ingress"
  retention_in_days = 30
  tags              = merge(local.common_tags, { System = "public-ingress" })
}

resource "aws_wafv2_web_acl_logging_configuration" "public_ingress" {
  resource_arn            = aws_wafv2_web_acl.public_ingress.arn
  log_destination_configs = [aws_cloudwatch_log_group.waf_public_ingress.arn]

  redacted_fields {
    single_header {
      name = "authorization"
    }
  }

  redacted_fields {
    single_header {
      name = "cookie"
    }
  }

  redacted_fields {
    query_string {}
  }
}

resource "aws_wafv2_web_acl_association" "observability_alb" {
  resource_arn = data.aws_lb.observability.arn
  web_acl_arn  = aws_wafv2_web_acl.public_ingress.arn
}

output "public_ingress_web_acl_arn" {
  description = "AWS WAF Web ACL protecting the shared public observability and ITSM ALB."
  value       = aws_wafv2_web_acl.public_ingress.arn
}

output "glpi_url" {
  description = "Public GLPI URL."
  value       = "https://glpi.cosmotechsolutions.com.br/"
}

output "kestra_url" {
  description = "Public Kestra URL."
  value       = "https://kestra.cosmotechsolutions.com.br/"
}
