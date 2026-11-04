# Seed only the isolated lab catalog. Runtime reservations own subsequent values;
# infrastructure reconciliation must never reset stock after processing orders.
resource "aws_dynamodb_table_item" "lab_inventory" {
  table_name = "aws-eks-istio-lab-dev-orders-data"
  hash_key   = "order_id"
  item = jsonencode({
    order_id = { S = "INVENTORY#LAB" }
    purpose  = { S = "simulated-lab-only" }
    stock = { M = {
      "LAB-SKU-001" = { N = "100" }
      "LAB-SKU-002" = { N = "50" }
    } }
  })
  lifecycle {
    prevent_destroy = true
    ignore_changes  = [item]
  }
}
