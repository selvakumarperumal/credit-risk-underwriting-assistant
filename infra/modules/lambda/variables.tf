# =============================================================================
# LAMBDA MODULE - INPUT VARIABLES
# =============================================================================
# These variables are passed from the root module to configure the Lambda
# function and API Gateway resources.
# =============================================================================

# -----------------------------------------------------------------------------
# REQUIRED VARIABLES (No defaults - must be provided)
# -----------------------------------------------------------------------------

variable "environment" {
  description = "Environment name"
  type        = string
  # Used for:
  # - Resource naming: credit-risk-assistant-{environment}
  # - Environment variable in Lambda: ENVIRONMENT
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  # Passed to Lambda as AWS_REGION_CUSTOM environment variable
  # Used for boto3 client configuration
}

variable "secrets_arn" {
  description = "ARN of the Secrets Manager secret"
  type        = string
  # This ARN is used for:
  # 1. IAM policy: Grant Lambda permission to read the secret
  # 2. Environment variable: Lambda fetches secrets using this ARN
}

# -----------------------------------------------------------------------------
# OPTIONAL VARIABLES (Have sensible defaults)
# -----------------------------------------------------------------------------

variable "memory_size" {
  description = "Lambda memory size in MB"
  type        = number
  default     = 512

  # Memory allocation affects performance:
  # - 512 MB is a good balance of cost and performance
  # - CPU scales proportionally with memory
  # - 512 MB ≈ 0.5 vCPU, 1024 MB ≈ 1 vCPU
  #
  # For AI workloads, consider increasing to 1024 MB or higher
  # if you experience slow cold starts or processing delays.
}

variable "timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 300 # 5 minutes

  # AI/LLM processing can take significant time:
  # - Gemini API calls: 5-30 seconds
  # - Complex analysis: up to 1-2 minutes
  # - 300 seconds provides headroom for complex requests
  #
  # API Gateway has a 30-second timeout by default, but HTTP APIs
  # can be configured for longer if needed.
  #
  # Maximum allowed: 900 seconds (15 minutes)
}
