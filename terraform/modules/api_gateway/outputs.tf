output "api_id" {
  description = "HTTP API Gateway ID."
  value       = aws_apigatewayv2_api.this.id
}

output "invoke_url" {
  description = "Orders API endpoint."
  value       = "${aws_apigatewayv2_stage.this.invoke_url}/orders"
}
