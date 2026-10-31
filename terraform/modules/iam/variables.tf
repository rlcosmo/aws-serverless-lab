variable "role_name" {
  description = "Name of the Lambda execution role."
  type        = string
}

variable "policy_statements" {
  description = "Explicit least-privilege inline policy statements."
  type = list(object({
    sid       = string
    actions   = list(string)
    resources = list(string)
    condition = optional(object({
      test     = string
      variable = string
      values   = list(string)
    }))
  }))
  default = []
}

variable "tags" {
  description = "Standard resource tags."
  type        = map(string)
  default     = {}
}
