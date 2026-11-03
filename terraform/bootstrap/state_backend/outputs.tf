output "state_bucket_name" {
  description = "Private, versioned S3 bucket used by the dev Terraform state backend."
  value       = aws_s3_bucket.terraform_state.bucket
}
