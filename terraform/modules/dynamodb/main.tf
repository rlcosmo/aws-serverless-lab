resource "aws_dynamodb_table" "orders" {
  # Item convention: ORDER#<id>/ORDER for orders and IDEMPOTENCY#<key>/STATE
  # for idempotency records. Only idempotency records should set expires_at.
  name                        = var.table_name
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "pk"
  range_key                   = "sk"
  deletion_protection_enabled = var.deletion_protection_enabled
  table_class                 = "STANDARD"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = var.point_in_time_recovery
  }

  server_side_encryption {
    enabled = true
  }

  tags = var.tags
}
