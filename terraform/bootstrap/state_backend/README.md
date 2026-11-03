# Terraform state backend bootstrap

This small bootstrap stack creates a private, versioned S3 bucket for the lab's Terraform state. It uses local state only for this one bucket so the DEV stack can migrate its existing local state without losing the local copy.

Run from this directory:

```bash
terraform init
terraform plan
terraform apply
```

The bucket blocks public access, enforces TLS, enables SSE-S3 and versioning, and has `prevent_destroy`. Do not delete historical state versions. The DEV backend uses S3 native lock files (`use_lockfile = true`). The local DEV state and backup remain in the ignored local directory after migration.
