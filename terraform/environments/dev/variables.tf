variable "aws_region" {
  description = "AWS region for the dev environment."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short project prefix used in resource names."
  type        = string
  default     = "aws-serverless-lab"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}$", var.project_name))
    error_message = "project_name must be lowercase and contain only letters, digits, and hyphens."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "tags" {
  description = "Additional tags applied to supported resources. Standard tags take precedence."
  type        = map(string)
  default     = {}
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention in days."
  type        = number
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653], var.log_retention_days)
    error_message = "log_retention_days must be a supported CloudWatch Logs retention period."
  }
}

variable "orders_table_deletion_protection" {
  description = "Protect the development orders table from accidental deletion."
  type        = bool
  default     = true
}

variable "orders_table_point_in_time_recovery" {
  description = "Enable DynamoDB point-in-time recovery. It can add cost; disabled by default in dev."
  type        = bool
  default     = false
}
