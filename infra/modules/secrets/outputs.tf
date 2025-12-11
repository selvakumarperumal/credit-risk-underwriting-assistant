# =============================================================================
# SECRETS MODULE - OUTPUT VALUES
# =============================================================================
# These outputs are used by other modules (Lambda) to access the secrets.
# =============================================================================

output "secrets_arn" {
  description = "ARN of the secrets manager secret"
  value       = aws_secretsmanager_secret.app_secrets.arn

  # The ARN is passed to the Lambda module for:
  # 1. IAM policy: Grant Lambda permission to read the secret
  # 2. Environment variable: Lambda uses this to retrieve secrets
  #
  # Format: arn:aws:secretsmanager:{region}:{account}:secret:{name}-{random}
}

output "secrets_name" {
  description = "Name of the secrets manager secret"
  value       = aws_secretsmanager_secret.app_secrets.name

  # The human-readable name of the secret.
  # Useful for:
  # - AWS Console navigation
  # - CLI commands: aws secretsmanager get-secret-value --secret-id {name}
}
