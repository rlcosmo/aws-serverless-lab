locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = merge(var.tags, {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  })

  producer_function_name = "${local.name_prefix}-orders-producer"
  consumer_function_name = "${local.name_prefix}-orders-consumer"
  producer_package_path  = "${path.root}/../../../dist/orders-producer.zip"
  consumer_package_path  = "${path.root}/../../../dist/orders-consumer.zip"
  lambda_timeout_seconds = 30
}
