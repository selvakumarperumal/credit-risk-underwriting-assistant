# =============================================================================
# ROOT VARIABLES - INPUT CONFIGURATION FOR THE INFRASTRUCTURE
# =============================================================================
# These variables are passed to the root module and distributed to child modules.
# Set values in terraform.tfvars or via environment variables (TF_VAR_*).
#
# Required variables (no defaults):
#   - gemini_api_key: Must be provided for Gemini AI integration
#
# Optional variables (have sensible defaults):
#   - aws_region, environment, gemini_model_name
# =============================================================================

# -----------------------------------------------------------------------------
# AWS INFRASTRUCTURE SETTINGS
# -----------------------------------------------------------------------------

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-south-1" # Mumbai - good latency for India-based users

  # Other common regions:
  # - us-east-1: Virginia (largest, most services)
  # - us-west-2: Oregon (good for US West Coast)
  # - eu-west-1: Ireland (good for European users)
}

variable "environment" {
  description = "Environment name (e.g., staging, production)"
  type        = string
  default     = "production"

  # Used for:
  # - Resource naming: credit-risk-assistant-{environment}
  # - Tagging: Environment tag on all resources
  # - Configuration: Different settings per environment (e.g., log retention)
}

# -----------------------------------------------------------------------------
# API KEYS AND CREDENTIALS
# -----------------------------------------------------------------------------
# SECURITY NOTE: Never commit actual values to version control!
# Use terraform.tfvars (gitignored) or environment variables.
# -----------------------------------------------------------------------------

variable "gemini_api_key" {
  description = "Gemini API key for AI-powered credit risk analysis"
  type        = string
  sensitive   = true # Hides value in logs and console output

  # How to obtain:
  # 1. Go to https://aistudio.google.com/app/apikey
  # 2. Create a new API key or use existing one
  # 3. Set via: export TF_VAR_gemini_api_key="your-key-here"
}

variable "gemini_model_name" {
  description = "Gemini model name for AI analysis"
  type        = string
  default     = "gemini-2.0-flash"

  # Available models:
  # - gemini-2.0-flash: Fast, efficient model (recommended)
  # - gemini-1.5-pro: More capable but slower
}
