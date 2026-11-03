variable "name_prefix" {
  description = "Resource naming prefix."
  type        = string
}

variable "environment" {
  description = "API Gateway deployment stage."
  type        = string
}

variable "lambda_arn" {
  description = "Producer Lambda ARN."
  type        = string
}

variable "lambda_function_name" {
  description = "Producer Lambda function name."
  type        = string
}

variable "tags" {
  description = "Standard resource tags."
  type        = map(string)
  default     = {}
}
