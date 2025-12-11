# =============================================================================
# CREDIT RISK UNDERWRITING ASSISTANT - ROOT TERRAFORM CONFIGURATION
# =============================================================================
# This is the main entry point for the infrastructure deployment.
# It orchestrates three modules: secrets, lambda, and frontend.
#
# Architecture Overview:
# ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
# │   Secrets   │────▶│   Lambda    │◀────│  Frontend   │
# │ (API Keys)  │     │ (Backend)   │     │ (React SPA) │
# └─────────────┘     └─────────────┘     └─────────────┘
#        │                   │                   │
#        ▼                   ▼                   ▼
#   AWS Secrets         API Gateway         CloudFront
#    Manager           + Lambda Fn           + S3
# =============================================================================

# -----------------------------------------------------------------------------
# TERRAFORM SETTINGS
# -----------------------------------------------------------------------------
# Defines the required Terraform version and provider dependencies.
# - terraform >= 1.0: Ensures compatibility with modern Terraform features
# - aws ~> 5.0: Uses AWS provider version 5.x for latest AWS service support
# - archive ~> 2.0: Used for creating Lambda deployment packages
# -----------------------------------------------------------------------------
terraform {
  required_version = ">= 1.0"

  required_providers {
    # AWS provider for all cloud resources (Lambda, S3, CloudFront, etc.)
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    # Archive provider for zipping Lambda function code
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  # ---------------------------------------------------------------------------
  # S3 BACKEND FOR STATE STORAGE
  # ---------------------------------------------------------------------------
  # PREREQUISITE: Run the bootstrap first!
  #   cd infra/bootstrap && terraform init && terraform apply
  #
  # Then uncomment this block and run: terraform init -migrate-state
  # ---------------------------------------------------------------------------
  backend "s3" {
    bucket         = "credit-risk-tf-state-selva"
    key            = "credit-risk-assistant/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# -----------------------------------------------------------------------------
# AWS PROVIDER CONFIGURATION (Primary Region)
# -----------------------------------------------------------------------------
# Configures the AWS provider with:
# - Dynamic region from variables (default: ap-south-1 / Mumbai)
# - Default tags applied to ALL resources created by this configuration
#
# Default tags help with:
# - Cost allocation and tracking
# - Resource identification
# - Automation and governance
# -----------------------------------------------------------------------------
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "credit-risk-assistant" # Project identifier for cost tracking
      Environment = var.environment         # staging/production differentiation
      ManagedBy   = "terraform"             # Indicates IaC-managed resources
    }
  }
}

# =============================================================================
# MODULE: SECRETS
# =============================================================================
# Manages sensitive configuration stored in AWS Secrets Manager.
# 
# Purpose:
# - Securely stores API keys (Google Gemini)
# - Enables rotation without redeploying Lambda
# - Provides audit trail for secret access
#
# Stored secrets:
# - GEMINI_API_KEY: Authentication for Gemini AI API
# - GEMINI_MODEL_NAME: Model to use for analysis
# =============================================================================
module "secrets" {
  source = "./modules/secrets"

  environment       = var.environment
  gemini_api_key    = var.gemini_api_key
  gemini_model_name = var.gemini_model_name
}

# =============================================================================
# MODULE: LAMBDA (Backend API)
# =============================================================================
# Deploys the backend API using AWS Lambda + API Gateway.
#
# Components created:
# - Lambda function: Runs the FastAPI application (Python 3.12)
# - API Gateway HTTP API: Provides REST endpoint with CORS support
# - IAM roles: Grants Lambda permission to access Secrets Manager
# - CloudWatch logs: Captures application and API Gateway logs
#
# The Lambda function:
# - Loads secrets from Secrets Manager on cold start
# - Processes credit risk analysis requests
# - Uses Mangum adapter to run FastAPI on Lambda
# =============================================================================
module "lambda" {
  source = "./modules/lambda"

  environment = var.environment
  aws_region  = var.aws_region
  secrets_arn = module.secrets.secrets_arn # ARN for secret access

  # Ensure secrets are created before Lambda (Lambda needs the ARN)
  depends_on = [module.secrets]
}

# =============================================================================
# MODULE: FRONTEND (Static Website Hosting)
# =============================================================================
# Deploys the React frontend using S3 + CloudFront.
#
# Components created:
# - S3 bucket: Stores compiled React assets (HTML, JS, CSS)
# - CloudFront distribution: Global CDN with HTTPS, caching, and compression
# - Origin Access Control: Secures S3 bucket (no public access)
#
# Features:
# - SPA routing: 404/403 errors return index.html for client-side routing
# - Compression: Gzip and Brotli compression for faster downloads
# - Cache policy: Long-term caching for static assets
# =============================================================================
module "frontend" {
  source = "./modules/frontend"

  environment = var.environment
  aws_region  = var.aws_region
  api_url     = module.lambda.api_gateway_url # Backend URL for frontend config

  # Pass AWS provider to frontend module
  providers = {
    aws = aws
  }

  # Ensure Lambda/API Gateway is created first (frontend needs API URL)
  depends_on = [module.lambda]
}
