resource "aws_cloudwatch_log_group" "lambda" {
  for_each = var.lambda_names

  name              = "/aws/lambda/${each.value}"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  for_each = var.lambda_error_alarm_names

  alarm_name          = "${each.value}-errors"
  alarm_description   = "One or more Lambda invocations failed in a five-minute period."
  namespace           = "AWS/Lambda"
  metric_name         = "Errors"
  dimensions          = { FunctionName = each.value }
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
  tags                = var.tags
}

resource "aws_cloudwatch_metric_alarm" "dead_letter_messages" {
  alarm_name          = "${var.dead_letter_queue_name}-messages-visible"
  alarm_description   = "At least one message is waiting in the orders dead-letter queue."
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  dimensions          = { QueueName = var.dead_letter_queue_name }
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
  tags                = var.tags
}
