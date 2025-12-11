# =============================================================================
# ROOT OUTPUTS - VALUES EXPORTED AFTER INFRASTRUCTURE DEPLOYMENT
# =============================================================================
# These outputs are displayed after 'terraform apply' and can be used by:
# - CI/CD pipelines for deployment automation
# - Frontend build process for API URL configuration
# - Operations team for monitoring and debugging
#
# Access outputs: terraform output <output_name>
# Get JSON: terraform output -json
# =============================================================================

# -----------------------------------------------------------------------------
# BACKEND API OUTPUTS
# -----------------------------------------------------------------------------

output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = module.lambda.api_gateway_url

  # This is the base URL for all API requests:
  # - POST {api_gateway_url}/api/analyze - Credit risk analysis
  # - GET  {api_gateway_url}/health - Health check
  #
  # Example: https://abc123xyz.execute-api.ap-south-1.amazonaws.com
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = module.lambda.function_name

  # Use this for:
  # - Viewing logs: aws logs tail /aws/lambda/{function_name}
  # - Invoking directly: aws lambda invoke --function-name {function_name}
  # - Monitoring: CloudWatch metrics under this function name
}

# -----------------------------------------------------------------------------
# FRONTEND OUTPUTS
# -----------------------------------------------------------------------------

output "cloudfront_url" {
  description = "CloudFront distribution URL for frontend"
  value       = module.frontend.cloudfront_url

  # This is the public URL for the React frontend application.
  # Example: https://d1234567abcdef.cloudfront.net
  #
  # For custom domain, add Route53 alias record pointing to this distribution.
}

output "s3_bucket_name" {
  description = "S3 bucket name for frontend assets"
  value       = module.frontend.s3_bucket_name

  # Use this to upload frontend build artifacts:
  # aws s3 sync ./frontend/dist s3://{bucket_name} --delete
  #
  # The bucket is not publicly accessible; CloudFront serves the content.
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (for cache invalidation)"
  value       = module.frontend.cloudfront_distribution_id

  # After deploying new frontend code, invalidate the CloudFront cache:
  # aws cloudfront create-invalidation \
  #   --distribution-id {distribution_id} \
  #   --paths "/*"
  #
  # This ensures users get the latest version immediately.
}
