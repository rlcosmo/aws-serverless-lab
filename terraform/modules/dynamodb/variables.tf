variable "table_name" {
  description = "Name of the single-table order store."
  type        = string
}

variable "deletion_protection_enabled" {
  description = "Protect the table from accidental deletion."
  type        = bool
  default     = true
}

variable "point_in_time_recovery" {
  description = "Enable DynamoDB point-in-time recovery. This can incur additional charges."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Standard resource tags."
  type        = map(string)
  default     = {}
}
