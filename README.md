# Credit Risk Underwriting Assistant

AI-powered assistant that reviews loan applicant profiles and generates comprehensive risk summary reports using LangChain, LangGraph, and Google Gemini.

## Features

- **12 Credit Risk Assessment Tools**: DTI, LTV, FOIR, EMI, DSCR, Credit Utilization, Employment Stability, Payment History, Credit Score Assessment, Collateral Coverage, Risk Classification, Total Risk Score
- **LangGraph ReAct Agent**: Uses the latest LangGraph `create_react_agent` pattern
- **Google Gemini Integration**: Powered by `langchain-google-genai`
- **FastAPI REST API**: Accepts raw text applicant profiles
- **AWS Serverless**: Lambda + API Gateway + CloudFront

---

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
cd src/backend
uv sync
```

### 2. Set Environment Variable

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export GEMINI_MODEL_NAME="gemini-2.0-flash"
```

### 3. Run the Server

```bash
cd src/backend
uv run uvicorn app.main:app --reload --port 8001
```

### 4. Test the API

```bash
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{"applicant_text": "Applicant: John Doe\nMonthly Income: ₹75,000\nExisting EMIs: ₹15,000\nLoan Amount: ₹20,00,000\nProperty Value: ₹30,00,000\nCredit Score: 720"}'
```

---

## AWS Deployment

### Prerequisites

- AWS Account with IAM credentials (configured locally via `aws configure`)
- Gemini API Key from [aistudio.google.com](https://aistudio.google.com/app/apikey)
- GitHub repository
- Terraform CLI installed locally

### Step 1: Bootstrap (One-Time Local Setup)

This creates an S3 bucket and DynamoDB table for Terraform state management:

```bash
cd infra/bootstrap
terraform init
terraform apply
```

After bootstrap completes, uncomment the S3 backend block in `infra/main.tf`.

### Step 2: Add GitHub Secrets

Go to **GitHub → Settings → Secrets → Actions** and add:

| Secret | Value |
|--------|-------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key |
| `GEMINI_API_KEY` | Your Gemini API key |
| `GEMINI_MODEL_NAME` | `gemini-2.0-flash` |

### Step 3: Deploy Infrastructure (Terraform)

1. Go to **GitHub → Actions → Terraform**
2. Click **Run workflow** → Select `plan` → Run
3. Review the plan output
4. Run again with `apply` to create infrastructure

This creates:
- Lambda function (backend)
- API Gateway (REST endpoint)
- S3 bucket (frontend hosting)
- CloudFront CDN
- Secrets Manager

### Step 4: Deploy Backend

1. Go to **GitHub → Actions → Deploy Backend**
2. Click **Run workflow**
3. Wait for completion

### Step 5: Deploy Frontend

1. Go to **GitHub → Actions → Deploy Frontend**
2. Click **Run workflow**
3. Your app is live at the CloudFront URL!

### Destroying Infrastructure

**Step 1: Destroy main infrastructure (GitHub Actions)**
1. Go to **GitHub → Actions → Terraform Destroy**
2. Type `destroy` to confirm
3. Click **Run workflow**

**Step 2: Destroy bootstrap resources (Local)**
```bash
cd infra/bootstrap
terraform destroy
```

> **Important:** Always destroy main infrastructure BEFORE bootstrap, otherwise Terraform state will be lost.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Service status |
| `/analyze` | POST | Analyze applicant |
| `/analyze/stream` | POST | Streaming analysis |

---

## Project Structure

```
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py       # FastAPI endpoints
│   │   │   ├── services.py   # LangGraph agent
│   │   │   ├── prompt.py     # System prompts
│   │   │   └── tools.py      # 12 credit risk tools
│   │   └── lambda_handler.py # AWS Lambda handler
│   └── frontend/             # React app
├── infra/                    # Terraform configuration
└── .github/workflows/        # CI/CD pipelines
```

---

## Available Tools

1. `compute_debt_to_income_ratio` - DTI calculation
2. `compute_loan_to_value_ratio` - LTV calculation
3. `compute_credit_utilization_ratio` - Credit usage
4. `compute_foir` - Fixed Obligation to Income Ratio
5. `compute_emi` - EMI calculator
6. `compute_dscr` - Debt Service Coverage Ratio
7. `assess_employment_stability` - Employment scoring
8. `compute_payment_history_score` - Payment analysis
9. `assess_credit_score` - Credit score interpretation
10. `compute_collateral_coverage_ratio` - Collateral assessment
11. `classify_risk_category` - Risk classification
12. `compute_total_risk_score` - Comprehensive score
