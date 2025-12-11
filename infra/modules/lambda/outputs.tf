# =============================================================================
# LAMBDA MODULE - OUTPUT VALUES
# =============================================================================
# These outputs are exported to the root module and can be used by:
# - Other modules (frontend needs api_gateway_url)
# - CI/CD pipelines for deployment
# - Root module outputs for user visibility
# =============================================================================

# -----------------------------------------------------------------------------
# LAMBDA FUNCTION OUTPUTS
# -----------------------------------------------------------------------------

output "function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.api.function_name

  # Use for:
  # - Viewing logs: aws logs tail /aws/lambda/{function_name} --follow
  # - Manual invocation: aws lambda invoke --function-name {function_name}
  # - Updating code: aws lambda update-function-code --function-name {function_name}
}

output "function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.api.arn

  # The ARN uniquely identifies this Lambda function.
  # Format: arn:aws:lambda:{region}:{account}:function:{function_name}
  #
  # Used for:
  # - Cross-account access policies
  # - EventBridge/CloudWatch event targets
  # - Step Functions integration
}

# -----------------------------------------------------------------------------
# API GATEWAY OUTPUTS
# -----------------------------------------------------------------------------

output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_api.http_api.api_endpoint

  # This is the public URL for the backend API.
  # Format: https://{api-id}.execute-api.{region}.amazonaws.com
  #
  # All API routes are relative to this base URL:
  # - POST {url}/api/analyze - Credit risk analysis endpoint
  # - GET  {url}/health - Health check endpoint
  #
  # This URL is passed to the frontend module for configuration.
}

output "api_gateway_id" {
  description = "API Gateway ID"
  value       = aws_apigatewayv2_api.http_api.id

  # The API ID is useful for:
  # - AWS CLI commands: aws apigatewayv2 get-api --api-id {id}
  # - CloudWatch metrics: ApiId dimension
  # - Manual stage deployment if auto_deploy is disabled
}
