# =============================================================================
# FRONTEND MODULE - STATIC WEBSITE HOSTING
# =============================================================================
# This module deploys the React frontend using S3 and CloudFront.
#
# Architecture:
# ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
# │     Client      │────▶│   CloudFront    │────▶│       S3        │
# │   (Browser)     │     │    (CDN Edge)   │     │  (Static Files) │
# └─────────────────┘     └─────────────────┘     └─────────────────┘
#                               │
#                               ├── HTTPS termination
#                               ├── Gzip/Brotli compression
#                               ├── Global edge caching
#                               └── SPA routing (404→index.html)
#
# Security:
# - S3 bucket is NOT publicly accessible
# - Only CloudFront can access S3 (via Origin Access Control)
# - All traffic is HTTPS (HTTP redirects to HTTPS)
# =============================================================================

# =============================================================================
# S3 BUCKET FOR STATIC ASSETS
# =============================================================================

# -----------------------------------------------------------------------------
# RANDOM SUFFIX FOR BUCKET NAME
# -----------------------------------------------------------------------------
# S3 bucket names must be globally unique. We append a random hex suffix
# to avoid naming conflicts across AWS accounts.
# -----------------------------------------------------------------------------
resource "random_id" "bucket_suffix" {
  byte_length = 4 # Generates 8 hex characters (e.g., "a1b2c3d4")
}

# -----------------------------------------------------------------------------
# S3 BUCKET
# -----------------------------------------------------------------------------
# Stores the compiled React application (HTML, JS, CSS, images).
# Files are uploaded via: aws s3 sync ./frontend/dist s3://{bucket_name}
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "frontend" {
  # Bucket name format: credit-risk-assistant-frontend-{env}-{random}
  # Example: credit-risk-assistant-frontend-production-a1b2c3d4
  bucket = "credit-risk-assistant-frontend-${var.environment}-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "credit-risk-assistant-frontend"
  }
}

# -----------------------------------------------------------------------------
# BLOCK ALL PUBLIC ACCESS
# -----------------------------------------------------------------------------
# The S3 bucket is completely private. CloudFront is the only way to access
# the files, which enforces HTTPS and allows for access logging.
# -----------------------------------------------------------------------------
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true # Block public ACLs
  block_public_policy     = true # Block public bucket policies
  ignore_public_acls      = true # Ignore existing public ACLs
  restrict_public_buckets = true # Restrict public bucket policies
}

# =============================================================================
# CLOUDFRONT CDN
# =============================================================================


# -----------------------------------------------------------------------------
# ORIGIN ACCESS CONTROL (OAC)
# -----------------------------------------------------------------------------
# OAC is the recommended way to grant CloudFront access to S3.
# It uses IAM-based authentication with SigV4 signing.
# Benefits over legacy OAI: Better security, supports KMS encryption.
# -----------------------------------------------------------------------------
resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "credit-risk-frontend-${var.environment}"
  description                       = "OAC for Credit Risk Assistant frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always" # Always sign requests to S3
  signing_protocol                  = "sigv4"  # Use AWS Signature Version 4
}

# -----------------------------------------------------------------------------
# CLOUDFRONT DISTRIBUTION
# -----------------------------------------------------------------------------
# The CDN that serves the frontend globally with edge caching.
# -----------------------------------------------------------------------------
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Credit Risk Assistant Frontend - ${var.environment}"
  default_root_object = "index.html" # Serve this when accessing root URL

  # Price class determines which edge locations are used:
  # - PriceClass_100: Only US, Canada, Europe (cheapest)
  # - PriceClass_200: US, Canada, Europe, Asia, Middle East, Africa (balanced)
  # - PriceClass_All: All edge locations (most expensive, lowest latency)
  price_class = "PriceClass_200"

  # ---------------------------------------------------------------------------
  # ORIGIN CONFIGURATION
  # ---------------------------------------------------------------------------
  # Defines where CloudFront fetches content from (our S3 bucket)
  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "S3Origin" # Internal identifier
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }

  # ---------------------------------------------------------------------------
  # DEFAULT CACHE BEHAVIOR
  # ---------------------------------------------------------------------------
  # Defines how CloudFront handles requests that don't match specific patterns
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"] # Read-only methods
    cached_methods         = ["GET", "HEAD"]            # Cache these methods
    target_origin_id       = "S3Origin"
    viewer_protocol_policy = "redirect-to-https" # Force HTTPS
    compress               = true                # Enable gzip/brotli compression

    # Use our custom cache policy (defined below)
    cache_policy_id = aws_cloudfront_cache_policy.frontend.id
    # AWS managed policy for S3 CORS origins
    origin_request_policy_id = "88a5eaf4-2fd4-4709-b370-b4c650ea3fcf"
  }

  # ---------------------------------------------------------------------------
  # SPA ROUTING - HANDLE 404 ERRORS
  # ---------------------------------------------------------------------------
  # React Router uses client-side routing. When a user navigates directly
  # to /dashboard or refreshes the page, S3 returns 404 (file not found).
  # These rules return index.html instead, letting React handle the route.
  # ---------------------------------------------------------------------------
  custom_error_response {
    error_code            = 404           # S3 returns 404 for unknown paths
    response_code         = 200           # Return HTTP 200 to browser
    response_page_path    = "/index.html" # Serve the React app
    error_caching_min_ttl = 0             # Don't cache error responses
  }

  custom_error_response {
    error_code            = 403 # S3 returns 403 for restricted paths
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 0
  }

  # ---------------------------------------------------------------------------
  # GEO RESTRICTIONS
  # ---------------------------------------------------------------------------
  # No geographic restrictions - allow access from all countries
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # ---------------------------------------------------------------------------
  # SSL/TLS CERTIFICATE
  # ---------------------------------------------------------------------------
  # Uses CloudFront's default certificate (*.cloudfront.net).
  # For custom domain, you would:
  # 1. Request ACM certificate in us-east-1
  # 2. Add aliases (e.g., ["app.example.com"])
  # 3. Reference the certificate ARN here
  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name = "credit-risk-assistant-cdn"
  }
}

# -----------------------------------------------------------------------------
# BUCKET POLICY - ALLOW CLOUDFRONT ACCESS
# -----------------------------------------------------------------------------
# Grants CloudFront permission to read objects from the bucket.
# Uses the new Origin Access Control (OAC) method instead of the legacy
# Origin Access Identity (OAI).
# -----------------------------------------------------------------------------
resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowCloudFrontAccess"
      Effect = "Allow"
      Principal = {
        Service = "cloudfront.amazonaws.com"
      }
      Action   = "s3:GetObject"                    # Read-only access
      Resource = "${aws_s3_bucket.frontend.arn}/*" # All objects in bucket
      Condition = {
        StringEquals = {
          # Only allow requests from THIS specific CloudFront distribution
          "AWS:SourceArn" = aws_cloudfront_distribution.frontend.arn
        }
      }
    }]
  })
  # Explicitly depend on the CloudFront distribution to ensure its ARN is available
  # and the distribution itself is created before the policy is applied.
  depends_on = [
    aws_cloudfront_distribution.frontend
  ]
}

# -----------------------------------------------------------------------------
# CACHE POLICY
# -----------------------------------------------------------------------------
# Defines how CloudFront caches and forwards requests.
# Optimized for static assets (HTML, JS, CSS, images).
# -----------------------------------------------------------------------------
resource "aws_cloudfront_cache_policy" "frontend" {
  name    = "credit-risk-frontend-cache-${var.environment}"
  comment = "Cache policy for Credit Risk Assistant frontend"

  # Time-to-live settings (in seconds)
  min_ttl     = 0        # Minimum cache time (can be overridden by headers)
  default_ttl = 86400    # Default: 1 day (when no Cache-Control header)
  max_ttl     = 31536000 # Maximum: 1 year (for immutable assets)

  # What's included in the cache key
  parameters_in_cache_key_and_forwarded_to_origin {
    # Don't use cookies for cache key (static assets don't need them)
    cookies_config {
      cookie_behavior = "none"
    }

    # Don't use headers for cache key (except Accept-Encoding)
    headers_config {
      header_behavior = "none"
    }

    # Don't use query strings for cache key
    # Note: If you use versioning like ?v=1.2.3, change to "whitelist" or "all"
    query_strings_config {
      query_string_behavior = "none"
    }

    # Enable compression (CloudFront compresses content on the fly)
    enable_accept_encoding_gzip   = true # Gzip compression (universal support)
    enable_accept_encoding_brotli = true # Brotli compression (better ratio)
  }
}
