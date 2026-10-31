output "table_name" {
  description = "Name of the orders and idempotency table."
  value       = aws_dynamodb_table.orders.name
}

output "table_arn" {
  description = "ARN of the orders and idempotency table."
  value       = aws_dynamodb_table.orders.arn
}
