output "orders_queue_url" {
  description = "URL of the main orders queue."
  value       = aws_sqs_queue.orders.url
}

output "orders_queue_arn" {
  description = "ARN of the main orders queue."
  value       = aws_sqs_queue.orders.arn
}

output "dead_letter_queue_arn" {
  description = "ARN of the orders dead-letter queue."
  value       = aws_sqs_queue.dead_letter.arn
}

output "dead_letter_queue_name" {
  description = "Name of the orders dead-letter queue."
  value       = aws_sqs_queue.dead_letter.name
}

output "dead_letter_queue_url" {
  description = "URL of the orders dead-letter queue."
  value       = aws_sqs_queue.dead_letter.url
}
