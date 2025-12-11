# =============================================================================
# SECRETS MODULE - INPUT VARIABLES
# =============================================================================
# These variables contain sensitive credentials passed from the root module.
# SECURITY: Never commit actual values to version control!
# =============================================================================

# -----------------------------------------------------------------------------
# ENVIRONMENT CONFIGURATION
# -----------------------------------------------------------------------------

variable "environment" {
  description = "Environment name"
  type        = string
  # Used in secret naming: credit-risk-assistant/{environment}/app-secrets
}

# -----------------------------------------------------------------------------
# GEMINI API CREDENTIALS
# -----------------------------------------------------------------------------

variable "gemini_api_key" {
  description = "Gemini API key for AI-powered credit risk analysis"
  type        = string
  sensitive   = true # Marked sensitive - won't appear in logs or output

  # How to obtain a Gemini API key:
  # 1. Visit https://aistudio.google.com/app/apikey
  # 2. Sign in with your Google account
  # 3. Click "Create API key" or use existing key
  # 4. Copy the key (shown only once!)
  #
  # Set via environment variable:
  # export TF_VAR_gemini_api_key="your-api-key-here"
}

variable "gemini_model_name" {
  description = "Gemini model name for AI analysis"
  type        = string
  default     = "gemini-2.0-flash"
}
