resource "aws_cloudwatch_dashboard" "serverless_lab" {
  dashboard_name = "aws-serverless-lab-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Lambda - Invocations"
          view   = "timeSeries"
          region = "us-east-1"
          period = 300
          metrics = [
            for name in sort(tolist(var.lambda_names)) :
            ["AWS/Lambda", "Invocations", "FunctionName", name]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Lambda - Errors"
          view   = "timeSeries"
          region = "us-east-1"
          period = 300
          metrics = [
            for name in sort(tolist(var.lambda_names)) :
            ["AWS/Lambda", "Errors", "FunctionName", name]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "Lambda - Duration"
          view   = "timeSeries"
          region = "us-east-1"
          period = 300
          metrics = [
            for name in sort(tolist(var.lambda_names)) :
            ["AWS/Lambda", "Duration", "FunctionName", name]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "SQS - Orders Queue"
          view   = "timeSeries"
          region = "us-east-1"
          period = 300
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", var.orders_queue_name],
            ["AWS/SQS", "ApproximateNumberOfMessagesNotVisible", "QueueName", var.orders_queue_name],
            ["AWS/SQS", "ApproximateAgeOfOldestMessage", "QueueName", var.orders_queue_name]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6
        properties = {
          title  = "SQS - Dead Letter Queue"
          view   = "timeSeries"
          region = "us-east-1"
          period = 300
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", var.dead_letter_queue_name]
          ]
        }
      }
    ]
  })
}
