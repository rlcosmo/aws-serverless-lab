output "aws_region" {
  description = "Region hosting the dev environment."
  value       = var.aws_region
}

output "orders_queue_url" {
  description = "URL for publishing order events."
  value       = module.sqs.orders_queue_url
}

output "orders_queue_arn" {
  description = "ARN for the main order queue."
  value       = module.sqs.orders_queue_arn
}

output "orders_dlq_arn" {
  description = "ARN for the order dead-letter queue."
  value       = module.sqs.dead_letter_queue_arn
}

output "orders_table_name" {
  description = "DynamoDB table prepared for order and idempotency records."
  value       = module.dynamodb.table_name
}

output "producer_function_name" {
  description = "Producer Lambda function name."
  value       = module.producer_lambda.function_name
}

output "consumer_function_name" {
  description = "Consumer Lambda function name."
  value       = module.consumer_lambda.function_name
}
