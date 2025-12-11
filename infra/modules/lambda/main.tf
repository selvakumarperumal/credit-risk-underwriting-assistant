# =============================================================================
# LAMBDA MODULE - SERVERLESS BACKEND DEPLOYMENT
# =============================================================================
# This module creates the backend infrastructure using AWS Lambda and API Gateway.
#
# Architecture:
# ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
# │   API Gateway   │────▶│     Lambda      │────▶│ Secrets Manager │
# │   (HTTP API)    │     │  (Python 3.12)  │     │   (API Keys)    │
# └─────────────────┘     └─────────────────┘     └─────────────────┘
#          │                      │
#          ▼                      ▼
#     CloudWatch             CloudWatch
#   (Access Logs)         (Function Logs)
#
# Request Flow:
# 1. Client sends HTTP request to API Gateway endpoint
# 2. API Gateway routes request to Lambda function
# 3. Lambda loads secrets and processes the credit risk analysis
# 4. Response is returned through API Gateway to client
# =============================================================================

# =============================================================================
# IAM ROLE AND POLICIES
# =============================================================================
# Lambda functions need an IAM role to:
# - Execute and create logs (AWSLambdaBasicExecutionRole)
# - Access secrets from Secrets Manager (custom policy)
# =============================================================================

# -----------------------------------------------------------------------------
# LAMBDA EXECUTION ROLE
# -----------------------------------------------------------------------------
# This IAM role is assumed by the Lambda function during execution.
# The trust policy allows only Lambda service to assume this role.
# -----------------------------------------------------------------------------
resource "aws_iam_role" "lambda_exec" {
  name = "credit-risk-lambda-${var.environment}"

  # Trust policy: Defines WHO can assume this role
  # Only the Lambda service (lambda.amazonaws.com) is allowed
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# -----------------------------------------------------------------------------
# BASIC LAMBDA EXECUTION POLICY
# -----------------------------------------------------------------------------
# Attaches AWS managed policy that grants:
# - logs:CreateLogGroup
# - logs:CreateLogStream
# - logs:PutLogEvents
# These are required for Lambda to write logs to CloudWatch.
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# -----------------------------------------------------------------------------
# SECRETS MANAGER ACCESS POLICY
# -----------------------------------------------------------------------------
# Custom inline policy allowing Lambda to read application secrets.
# Principle of least privilege: Only GetSecretValue, only specific secret ARN.
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy" "lambda_secrets" {
  name = "secrets-access"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "secretsmanager:GetSecretValue" # Read-only access to secrets
      ]
      Resource = var.secrets_arn # Restricted to our specific secret
    }]
  })
}

# =============================================================================
# LAMBDA FUNCTION
# =============================================================================
# The core compute resource that runs the FastAPI backend application.
# Uses Mangum adapter to translate API Gateway events to ASGI format.
#
# DEPLOYMENT STRATEGY:
# - Terraform creates the Lambda function with placeholder code
# - GitHub Actions deploys the real application code
# - This separation allows infrastructure and code to be managed independently
# =============================================================================

# -----------------------------------------------------------------------------
# PLACEHOLDER DEPLOYMENT PACKAGE
# -----------------------------------------------------------------------------
# Creates a minimal zip file for initial Lambda creation.
# Real application code is deployed via GitHub Actions using:
#   aws lambda update-function-code --function-name ... --zip-file ...
# -----------------------------------------------------------------------------
data "archive_file" "lambda_placeholder" {
  type        = "zip"
  output_path = "${path.module}/placeholder.zip"

  source {
    content  = <<-EOF
      def handler(event, context):
          return {
              "statusCode": 503,
              "body": "Application not deployed yet. Run GitHub Actions deploy-backend workflow."
          }
    EOF
    filename = "lambda_handler.py"
  }
}

resource "aws_lambda_function" "api" {
  # ---------------------------------------------------------------------------
  # DEPLOYMENT PACKAGE (Placeholder - real code via GitHub Actions)
  # ---------------------------------------------------------------------------
  filename         = data.archive_file.lambda_placeholder.output_path
  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256

  # ---------------------------------------------------------------------------
  # FUNCTION CONFIGURATION
  # ---------------------------------------------------------------------------
  function_name = "credit-risk-assistant-${var.environment}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_handler.handler" # File: lambda_handler.py, Function: handler
  runtime       = "python3.12"             # Python version matching backend code

  # ---------------------------------------------------------------------------
  # RESOURCE ALLOCATION
  # ---------------------------------------------------------------------------
  memory_size = var.memory_size # Default: 512 MB (also affects CPU allocation)
  timeout     = var.timeout     # Default: 300 seconds (5 min for AI processing)
  # Note: Lambda CPU scales proportionally with memory
  # 512 MB ≈ 0.5 vCPU, 1769 MB = 1 vCPU, 3538 MB = 2 vCPU

  # ---------------------------------------------------------------------------
  # ENVIRONMENT VARIABLES
  # ---------------------------------------------------------------------------
  # These are available to the application via os.environ
  environment {
    variables = {
      ENVIRONMENT       = var.environment # staging/production
      SECRETS_ARN       = var.secrets_arn # ARN to fetch secrets
      AWS_REGION_CUSTOM = var.aws_region  # For boto3 client config
      # Note: GEMINI_API_KEY is fetched from Secrets Manager at runtime
    }
  }

  # Ignore changes to filename/source_code_hash since GitHub Actions manages code
  lifecycle {
    ignore_changes = [filename, source_code_hash]
  }

  tags = {
    Name = "credit-risk-assistant-api"
  }
}

# =============================================================================
# API GATEWAY HTTP API
# =============================================================================
# HTTP API (v2) is the modern, cheaper, faster alternative to REST API.
# Features used: Lambda proxy integration, CORS, auto-deploy staging.
# Pricing: ~$1.00 per million requests (vs $3.50 for REST API)
# =============================================================================

# -----------------------------------------------------------------------------
# HTTP API DEFINITION
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_api" "http_api" {
  name          = "credit-risk-api-${var.environment}"
  protocol_type = "HTTP" # HTTP API (simpler, cheaper than REST API)

  # ---------------------------------------------------------------------------
  # CORS CONFIGURATION
  # ---------------------------------------------------------------------------
  # Cross-Origin Resource Sharing settings for browser-based clients.
  # Required because frontend (CloudFront) and API have different domains.
  cors_configuration {
    allow_origins = ["*"]                             # TODO: Restrict to CloudFront domain in production
    allow_methods = ["GET", "POST", "OPTIONS"]        # Supported HTTP methods
    allow_headers = ["Content-Type", "Authorization"] # Allowed request headers
    max_age       = 3600                              # Browser caches preflight response for 1 hour
  }
}

# -----------------------------------------------------------------------------
# LAMBDA INTEGRATION
# -----------------------------------------------------------------------------
# Connects API Gateway to Lambda function using AWS_PROXY integration.
# AWS_PROXY: API Gateway passes the entire request to Lambda and returns
# the Lambda response directly to the client.
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY" # Lambda proxy integration
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0" # Newer, simpler event format
}

# -----------------------------------------------------------------------------
# DEFAULT ROUTE (CATCH-ALL)
# -----------------------------------------------------------------------------
# Routes ALL requests to the Lambda function.
# FastAPI handles the actual path routing internally.
# This is simpler than defining individual routes in API Gateway.
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "$default" # Matches any HTTP method and path
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# -----------------------------------------------------------------------------
# AUTO-DEPLOY STAGE
# -----------------------------------------------------------------------------
# The $default stage with auto_deploy means changes to routes/integrations
# are automatically deployed without manual intervention.
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default" # Default stage (no stage prefix in URL)
  auto_deploy = true       # Automatically deploy on changes
}

# =============================================================================
# LAMBDA PERMISSION
# =============================================================================

# -----------------------------------------------------------------------------
# API GATEWAY INVOKE PERMISSION
# -----------------------------------------------------------------------------
# Grants API Gateway permission to invoke the Lambda function.
# Without this, API Gateway would receive "Access Denied" errors.
# -----------------------------------------------------------------------------
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
  # The /*/*" allows any stage and any route to invoke Lambda
}
