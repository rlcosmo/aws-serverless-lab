output "log_group_names" {
  description = "Managed Lambda log group names keyed by function name."
  value       = { for name, group in aws_cloudwatch_log_group.lambda : name => group.name }
}

output "log_group_arns" {
  description = "Managed Lambda log group ARNs keyed by function name."
  value       = { for name, group in aws_cloudwatch_log_group.lambda : name => group.arn }
}
