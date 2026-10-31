resource "aws_lambda_function" "this" {
  function_name    = var.function_name
  description      = var.description
  role             = var.role_arn
  runtime          = "python3.12"
  handler          = var.handler
  filename         = var.package_path
  source_code_hash = filebase64sha256(var.package_path)
  timeout          = var.timeout
  memory_size      = var.memory_size
  architectures    = ["x86_64"]

  environment {
    variables = var.environment_variables
  }

  logging_config {
    log_format            = "JSON"
    application_log_level = "INFO"
    system_log_level      = "WARN"
  }

  tags = var.tags
}

resource "aws_lambda_event_source_mapping" "sqs" {
  count = var.event_source_queue_arn == null ? 0 : 1

  event_source_arn                   = var.event_source_queue_arn
  function_name                      = aws_lambda_function.this.arn
  batch_size                         = var.event_source_batch_size
  function_response_types            = ["ReportBatchItemFailures"]
  maximum_batching_window_in_seconds = 0
  enabled                            = true
}
