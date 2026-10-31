resource "aws_sqs_queue" "dead_letter" {
  name                      = "${var.name_prefix}-orders-dlq"
  message_retention_seconds = var.dlq_retention_seconds
  sqs_managed_sse_enabled   = true

  tags = var.tags
}

resource "aws_sqs_queue" "orders" {
  name                       = "${var.name_prefix}-orders"
  visibility_timeout_seconds = var.consumer_timeout_seconds * 6
  message_retention_seconds  = var.source_retention_seconds
  receive_wait_time_seconds  = 20
  sqs_managed_sse_enabled    = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dead_letter.arn
    maxReceiveCount     = var.max_receive_count
  })

  tags = var.tags
}

resource "aws_sqs_queue_redrive_allow_policy" "dead_letter" {
  queue_url = aws_sqs_queue.dead_letter.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [aws_sqs_queue.orders.arn]
  })
}
