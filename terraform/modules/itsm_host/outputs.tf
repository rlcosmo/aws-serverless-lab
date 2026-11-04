output "instance_id" {
  description = "Private EC2 instance managed through Systems Manager."
  value       = aws_instance.this.id
}

output "backup_plan_id" {
  value = aws_backup_plan.this.id
}

output "backup_role_arn" {
  value = aws_iam_role.backup.arn
}

output "private_ip" {
  description = "Private address of the ITSM host."
  value       = aws_instance.this.private_ip
}

output "instance_role_arn" {
  description = "IAM role assumed by the EC2 instance profile."
  value       = aws_iam_role.instance.arn
}

output "security_group_id" {
  description = "Security group with no ingress rules."
  value       = aws_security_group.this.id
}
