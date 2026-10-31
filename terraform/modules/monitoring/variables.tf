variable "lambda_names" {
  description = "Lambda function names whose log groups are managed here."
  type        = set(string)
}

variable "dead_letter_queue_name" {
  description = "Dead-letter queue to monitor for any visible messages."
  type        = string
}

variable "lambda_error_alarm_names" {
  description = "Lambda function names to alarm on when invocation errors occur."
  type        = set(string)
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

variable "tags" {
  description = "Standard resource tags."
  type        = map(string)
  default     = {}
}
