# =============================================================================
# FRONTEND MODULE - OUTPUT VALUES
# =============================================================================
# These outputs are exported to the root module and used for:
# - CI/CD deployment scripts
# - Displaying URLs after terraform apply
# - Cache invalidation after deployments
# =============================================================================

# -----------------------------------------------------------------------------
# S3 BUCKET OUTPUTS
# -----------------------------------------------------------------------------

output "s3_bucket_name" {
  description = "S3 bucket name for frontend assets"
  value       = aws_s3_bucket.frontend.id

  # Use this to upload the React build:
  # aws s3 sync ./frontend/dist s3://{bucket_name} --delete
  #
  # The --delete flag removes files in S3 that aren't in the local build.
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.frontend.arn

  # The ARN uniquely identifies this S3 bucket.
  # Format: arn:aws:s3:::{bucket-name}
  #
  # Useful for:
  # - IAM policies that reference the bucket
  # - Cross-account access configurations
}

# -----------------------------------------------------------------------------
# CLOUDFRONT OUTPUTS
# -----------------------------------------------------------------------------

output "cloudfront_url" {
  description = "CloudFront distribution URL"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"

  # This is the public URL for the frontend application.
  # Example: https://d1234567abcdef.cloudfront.net
  #
  # Share this URL with users to access the Credit Risk Assistant.
  # For custom domain, create a Route53 ALIAS record pointing to
  # the cloudfront_domain_name (below).
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (for cache invalidation)"
  value       = aws_cloudfront_distribution.frontend.id

  # After deploying new frontend code, invalidate the cache to ensure
  # users see the latest version immediately:
  #
  # aws cloudfront create-invalidation \
  #   --distribution-id {distribution_id} \
  #   --paths "/*"
  #
  # Invalidations are free for the first 1000/month, then $0.005 per path.
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name

  # The raw CloudFront domain without https:// prefix.
  # Example: d1234567abcdef.cloudfront.net
  #
  # Use this for:
  # - Route53 ALIAS records (for custom domains)
  # - API Gateway CORS allow_origins configuration
}
