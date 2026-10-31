variable "name_prefix" {
  description = "Prefix used for queue names."
  type        = string
}

variable "consumer_timeout_seconds" {
  description = "Timeout configured on the consumer Lambda."
  type        = number
  default     = 30

  validation {
    condition     = var.consumer_timeout_seconds >= 1 && var.consumer_timeout_seconds <= 900
    error_message = "consumer_timeout_seconds must be between 1 and 900."
  }
}

variable "max_receive_count" {
  description = "Receive attempts before SQS moves a message to the DLQ."
  type        = number
  default     = 5

  validation {
    condition     = var.max_receive_count >= 1
    error_message = "max_receive_count must be at least 1."
  }
}

variable "source_retention_seconds" {
  description = "Main queue message retention."
  type        = number
  default     = 345600

  validation {
    condition     = var.source_retention_seconds >= 60 && var.source_retention_seconds <= 1209600
    error_message = "source_retention_seconds must be between 60 and 1209600."
  }
}

variable "dlq_retention_seconds" {
  description = "Dead-letter queue message retention."
  type        = number
  default     = 1209600

  validation {
    condition     = var.dlq_retention_seconds >= 60 && var.dlq_retention_seconds <= 1209600
    error_message = "dlq_retention_seconds must be between 60 and 1209600."
  }
}

variable "tags" {
  description = "Standard resource tags."
  type        = map(string)
  default     = {}
}
