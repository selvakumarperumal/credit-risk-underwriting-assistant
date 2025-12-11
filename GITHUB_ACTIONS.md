# GitHub Actions CI/CD Flow

Complete CI/CD pipeline documentation for deploying the Credit Risk Underwriting Assistant.

## Workflows Overview

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **Terraform** | Manual | Create/update AWS infrastructure |
| **Terraform Destroy** | Manual | Tear down AWS infrastructure |
| **Deploy Backend** | Manual | Deploy Lambda function code |
| **Deploy Frontend** | Manual | Build and deploy React app |

> **Note:** All workflows are manually triggered via `workflow_dispatch` for controlled deployments.

---

## Required GitHub Secrets

Go to **GitHub → Settings → Secrets → Actions** and add:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `GEMINI_API_KEY` | Google Gemini AI API key |
| `GEMINI_MODEL_NAME` | Model name (e.g., `gemini-2.0-flash`) |

---

## 1. Terraform Workflow

**File:** `.github/workflows/terraform.yml`

Creates all AWS infrastructure using Terraform.

### How to Run

1. Go to **Actions → Terraform**
2. Click **Run workflow**
3. Select action: `plan` or `apply`

### Jobs

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Validate   │───▶│    Plan     │───▶│   Apply     │
│             │    │             │    │ (if apply)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

| Job | What it does |
|-----|--------------|
| **Validate** | Format check, `terraform init`, `terraform validate` |
| **Plan** | Generate execution plan, save as artifact |
| **Apply** | Apply plan (only if `apply` action selected) |

### Resources Created

- Lambda function: `credit-risk-assistant-production`
- API Gateway: `credit-risk-api-production`
- S3 bucket: `credit-risk-assistant-frontend-production-*`
- CloudFront distribution
- Secrets Manager secret

---

## 2. Terraform Destroy Workflow

**File:** `.github/workflows/terraform-destroy.yml`

Tears down all AWS infrastructure.

### How to Run

1. Go to **Actions → Terraform Destroy**
2. Type `destroy` to confirm
3. Click **Run workflow**

> ⚠️ **Warning:** This destroys ALL infrastructure. The state is stored in S3, so this works correctly across workflow runs.

---

## 3. Deploy Backend Workflow

**File:** `.github/workflows/deploy-backend.yml`

Builds and deploys the Python FastAPI backend to AWS Lambda.

### How to Run

1. Go to **Actions → Deploy Backend**
2. Click **Run workflow**

### Jobs

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Test     │───▶│    Build    │───▶│   Deploy    │
│             │    │ lambda.zip  │    │  to Lambda  │
└─────────────┘    └─────────────┘    └─────────────┘
```

| Job | What it does |
|-----|--------------|
| **Test** | Install deps with `uv`, verify imports |
| **Build** | Install deps to package dir, create `lambda.zip` |
| **Deploy** | Upload to Lambda, wait for update, smoke test |

### Build Details

```bash
# Uses uv for dependency management
uv pip install --target lambda_package .

# Creates zip with:
# - All Python dependencies
# - app/ directory
# - lambda_handler.py
```

---

## 4. Deploy Frontend Workflow

**File:** `.github/workflows/deploy-frontend.yml`

Builds the React app and deploys to S3 + CloudFront.

### How to Run

1. Go to **Actions → Deploy Frontend**
2. Click **Run workflow**

### Jobs

```
┌───────────────────────────────────────────────────────┐
│                  Build and Deploy                     │
│                                                       │
│  1. Get infra values from AWS (API URL, S3, CF)      │
│  2. npm ci → npm run lint → npm run build            │
│  3. Upload to S3                                      │
│  4. Invalidate CloudFront cache                      │
└───────────────────────────────────────────────────────┘
```

### Automatic Value Detection

The workflow **automatically fetches** infrastructure values from AWS:

| Value | How it's fetched |
|-------|------------------|
| API Gateway URL | `aws apigatewayv2 get-apis` by name |
| S3 Bucket | `aws s3api list-buckets` by prefix |
| CloudFront ID | `aws cloudfront list-distributions` by comment |

This means you **don't need** to manually configure these as secrets!

### Environment Variable

```bash
VITE_API_URL=https://xxxxx.execute-api.ap-south-1.amazonaws.com
```

This is set at build time and baked into the frontend bundle.

---

## Complete Deployment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        ONE-TIME SETUP                           │
├─────────────────────────────────────────────────────────────────┤
│  1. Bootstrap (local)                                           │
│     cd infra/bootstrap && terraform init && terraform apply    │
│                                                                 │
│  2. Add GitHub Secrets                                          │
│     AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,                   │
│     GEMINI_API_KEY, GEMINI_MODEL_NAME                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT (GitHub Actions)                │
├─────────────────────────────────────────────────────────────────┤
│  1. Terraform (plan → apply)                                    │
│     Creates: Lambda, API Gateway, S3, CloudFront, Secrets      │
│                                                                 │
│  2. Deploy Backend                                              │
│     Uploads real code to Lambda function                        │
│                                                                 │
│  3. Deploy Frontend                                             │
│     Builds React app, uploads to S3, invalidates CloudFront    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TEARDOWN                                │
├─────────────────────────────────────────────────────────────────┤
│  1. Terraform Destroy (GitHub Actions)                          │
│     Destroys: Lambda, API Gateway, S3, CloudFront, Secrets     │
│                                                                 │
│  2. Bootstrap destroy (local)                                   │
│     cd infra/bootstrap && terraform destroy                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture Deployed

```
                    ┌─────────────────┐
                    │     Users       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   CloudFront    │
                    │   (CDN Cache)   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
     ┌─────────────────┐           ┌─────────────────┐
     │   S3 Bucket     │           │  API Gateway    │
     │  (React App)    │           │   (HTTP API)    │
     └─────────────────┘           └────────┬────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │     Lambda      │
                                   │  (FastAPI +     │
                                   │   Mangum)       │
                                   └────────┬────────┘
                                            │
                        ┌───────────────────┴───────────────────┐
                        │                                       │
                        ▼                                       ▼
               ┌─────────────────┐                     ┌─────────────────┐
               │ Secrets Manager │                     │  Gemini AI API  │
               │ (API Keys)      │                     │  (Google)       │
               └─────────────────┘                     └─────────────────┘
```

---

## Terraform State Management

State is stored in **S3** (created by bootstrap):

| Resource | Name |
|----------|------|
| S3 Bucket | `credit-risk-tf-state-selva` |
| DynamoDB Table | `terraform-locks` |
| State Key | `credit-risk-assistant/terraform.tfstate` |

This ensures that Terraform apply and destroy workflows share the same state.
