variable "function_name" {
  description = "Lambda function name."
  type        = string
}

variable "description" {
  description = "Short function description."
  type        = string
}

variable "handler" {
  description = "Python module and handler symbol."
  type        = string
}

variable "package_path" {
  description = "Path to a prebuilt deployment ZIP. Package creation is outside this module."
  type        = string
}

variable "role_arn" {
  description = "Execution role ARN."
  type        = string
}

variable "timeout" {
  description = "Lambda timeout in seconds."
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Lambda memory allocation in MiB."
  type        = number
  default     = 128
}

variable "environment_variables" {
  description = "Non-secret Lambda environment variables."
  type        = map(string)
  default     = {}
}

variable "event_source_queue_arn" {
  description = "Optional SQS queue ARN for a Lambda event source mapping."
  type        = string
  default     = null
}

variable "event_source_batch_size" {
  description = "Maximum SQS records per Lambda invocation."
  type        = number
  default     = 10

  validation {
    condition     = var.event_source_batch_size >= 1 && var.event_source_batch_size <= 10
    error_message = "event_source_batch_size must be between 1 and 10 for this SQS mapping."
  }
}

variable "tags" {
  description = "Standard resource tags."
  type        = map(string)
  default     = {}
}
