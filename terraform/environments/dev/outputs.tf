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


output "orders_api_url" {
  description = "HTTP endpoint for creating orders."
  value       = module.api_gateway.invoke_url
}

output "orders_api_id" {
  description = "HTTP API Gateway ID."
  value       = module.api_gateway.api_id
}

output "cloudwatch_dashboard_name" {
  description = "CloudWatch dashboard for the Serverless Lab."
  value       = module.monitoring.dashboard_name
}
