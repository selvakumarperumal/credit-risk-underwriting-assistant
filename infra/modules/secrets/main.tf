# =============================================================================
# SECRETS MODULE - AWS SECRETS MANAGER CONFIGURATION
# =============================================================================
# This module manages sensitive credentials stored in AWS Secrets Manager.
#
# Why Secrets Manager instead of environment variables?
# 1. Security: Secrets are encrypted at rest and in transit
# 2. Rotation: Secrets can be rotated without redeploying Lambda
# 3. Audit: CloudTrail logs all secret access attempts
# 4. Centralized: Single source of truth for credentials
#
# Stored Secrets:
# - GEMINI_API_KEY: Authentication key for Google Gemini AI API
# - GEMINI_MODEL_NAME: Model to use for analysis
# =============================================================================

# -----------------------------------------------------------------------------
# SECRETS MANAGER SECRET (Container)
# -----------------------------------------------------------------------------
# Creates the secret "container" - the actual secret values are stored
# in a separate version resource below.
# -----------------------------------------------------------------------------
resource "aws_secretsmanager_secret" "app_secrets" {
  # Secret name follows AWS recommended naming convention:
  # {application}/{environment}/{secret-type}
  name        = "credit-risk-assistant/${var.environment}/app-secrets"
  description = "API keys and credentials for Credit Risk Assistant"

  # Recovery window: Days to wait before permanent deletion
  # - 0: Immediate deletion (use for dev/testing, NOT production)
  # - 7-30: Recommended for production (recovery grace period)
  # WARNING: Set to 7+ for production to prevent accidental data loss!
  recovery_window_in_days = 0 # Set to 7+ for production

  tags = {
    Name = "credit-risk-assistant-secrets"
  }
}

# -----------------------------------------------------------------------------
# SECRET VERSION (Actual Values)
# -----------------------------------------------------------------------------
# Stores the actual secret values as a JSON object.
# Each update creates a new version (previous versions are retained).
# -----------------------------------------------------------------------------
resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id

  # Store secrets as JSON for structured access
  # Lambda retrieves this and parses it to get individual values
  secret_string = jsonencode({
    # Required: Gemini API key for AI-powered credit risk analysis
    GEMINI_API_KEY    = var.gemini_api_key
    GEMINI_MODEL_NAME = var.gemini_model_name
  })

  # Note: When you update secret values, Terraform creates a new version.
  # The Lambda function always retrieves the AWSCURRENT version.
}

# =============================================================================
# HOW LAMBDA ACCESSES SECRETS
# =============================================================================
# The Lambda function retrieves secrets at runtime using:
#
# import boto3
# import json
#
# def get_secrets(secret_arn):
#     client = boto3.client('secretsmanager')
#     response = client.get_secret_value(SecretId=secret_arn)
#     return json.loads(response['SecretString'])
#
# secrets = get_secrets(os.environ['SECRETS_ARN'])
# gemini_api_key = secrets['GEMINI_API_KEY']
# gemini_model_name = secrets['GEMINI_MODEL_NAME']
# =============================================================================
