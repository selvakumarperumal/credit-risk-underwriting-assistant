# =============================================================================
# FRONTEND MODULE - PROVIDER CONFIGURATION AND VARIABLES
# =============================================================================
# This file contains provider requirements and input variables for the
# frontend module.
# =============================================================================

# -----------------------------------------------------------------------------
# TERRAFORM PROVIDER REQUIREMENTS
# -----------------------------------------------------------------------------
# This module requires the default AWS provider for S3 bucket creation.
# CloudFront is a global service and works with the default provider.
# Note: If custom SSL certificates are needed later, add us-east-1 provider.
# -----------------------------------------------------------------------------
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

# =============================================================================
# INPUT VARIABLES
# =============================================================================

variable "environment" {
  description = "Environment name"
  type        = string

  # Used for:
  # - S3 bucket naming: credit-risk-assistant-frontend-{environment}-{suffix}
  # - CloudFront comment: "Credit Risk Assistant Frontend - {environment}"
  # - Cache policy naming
}

variable "aws_region" {
  description = "AWS region"
  type        = string

  # The primary region where the S3 bucket is created.
  # Note: CloudFront will cache content at edge locations worldwide
  # regardless of the S3 bucket's region.
}

variable "api_url" {
  description = "Backend API URL for CORS configuration"
  type        = string

  # The API Gateway URL from the Lambda module.
  # This can be used for:
  # - Frontend configuration (write to config.js during deployment)
  # - Future CloudFront-level CORS headers
  # - Lambda@Edge functions that need to proxy to the API
}
