module "sqs" {
  source = "../../modules/sqs"

  name_prefix              = local.name_prefix
  consumer_timeout_seconds = local.lambda_timeout_seconds
  tags                     = local.common_tags
}

module "dynamodb" {
  source = "../../modules/dynamodb"

  table_name                  = "${local.name_prefix}-orders"
  deletion_protection_enabled = var.orders_table_deletion_protection
  point_in_time_recovery      = var.orders_table_point_in_time_recovery
  tags                        = local.common_tags
}

module "monitoring" {
  source = "../../modules/monitoring"

  lambda_names             = [local.producer_function_name, local.consumer_function_name]
  dead_letter_queue_name   = module.sqs.dead_letter_queue_name
  lambda_error_alarm_names = [local.producer_function_name, local.consumer_function_name]
  log_retention_days       = var.log_retention_days
  tags                     = local.common_tags
}

module "producer_iam" {
  source = "../../modules/iam"

  role_name = "${local.producer_function_name}-role"
  tags      = local.common_tags
  policy_statements = [
    {
      sid       = "PublishOrders"
      actions   = ["sqs:SendMessage"]
      resources = [module.sqs.orders_queue_arn]
      condition = null
    },
    {
      sid       = "WriteProducerLogs"
      actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      resources = ["${trimsuffix(module.monitoring.log_group_arns[local.producer_function_name], ":*")}:log-stream:*"]
      condition = null
    }
  ]
}

module "consumer_iam" {
  source = "../../modules/iam"

  role_name = "${local.consumer_function_name}-role"
  tags      = local.common_tags
  policy_statements = [
    {
      sid       = "ConsumeOrders"
      actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes", "sqs:ChangeMessageVisibility"]
      resources = [module.sqs.orders_queue_arn]
      condition = null
    },
    {
      sid       = "ManageIdempotencyRecords"
      actions   = ["dynamodb:GetItem", "dynamodb:UpdateItem"]
      resources = [module.dynamodb.table_arn]
      condition = {
        test     = "ForAllValues:StringLike"
        variable = "dynamodb:LeadingKeys"
        values   = ["IDEMPOTENCY#*"]
      }
    },
    {
      sid       = "WriteConsumerLogs"
      actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
      resources = ["${trimsuffix(module.monitoring.log_group_arns[local.consumer_function_name], ":*")}:log-stream:*"]
      condition = null
    }
  ]
}

module "producer_lambda" {
  source = "../../modules/lambda"

  function_name = local.producer_function_name
  description   = "Validates order requests and publishes order.created events."
  handler       = "orders.producer.handler.handler"
  package_path  = local.producer_package_path
  role_arn      = module.producer_iam.role_arn
  timeout       = local.lambda_timeout_seconds
  environment_variables = {
    ORDERS_QUEUE_URL = module.sqs.orders_queue_url
  }
  tags = local.common_tags
}

module "consumer_lambda" {
  source = "../../modules/lambda"

  function_name           = local.consumer_function_name
  description             = "Consumes and validates order events from SQS."
  handler                 = "orders.consumer.handler.handler"
  package_path            = local.consumer_package_path
  role_arn                = module.consumer_iam.role_arn
  timeout                 = local.lambda_timeout_seconds
  event_source_queue_arn  = module.sqs.orders_queue_arn
  event_source_batch_size = 10
  environment_variables = {
    ORDERS_TABLE_NAME = module.dynamodb.table_name
  }
  tags = local.common_tags
}
