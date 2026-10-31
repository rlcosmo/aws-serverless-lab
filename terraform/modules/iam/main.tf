resource "aws_iam_role" "lambda" {
  name = var.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "lambda" {
  name = "${var.role_name}-inline"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      for statement in var.policy_statements : merge(
        {
          Sid      = statement.sid
          Effect   = "Allow"
          Action   = statement.actions
          Resource = statement.resources
        },
        statement.condition == null ? {} : {
          Condition = {
            (statement.condition.test) = {
              (statement.condition.variable) = statement.condition.values
            }
          }
        }
      )
    ]
  })
}
