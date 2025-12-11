"""
Credit Risk Underwriting Assistant - FastAPI Endpoints
=======================================================

This module provides REST API endpoints for the credit risk
underwriting agent using dependency injection (no global state).
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("../../../.env", override=True)

# Add the backend directory to sys.path for 'app' module imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from app.services import CreditRiskAgentService


# =============================================================================
# Configuration with Pydantic Settings (Environment Variables)
# =============================================================================

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    gemini_api_key: str
    gemini_model_name: str

@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Using lru_cache ensures settings are only loaded once,
    making this effectively a singleton without mutable global state.
    """
    return Settings()


# =============================================================================
# Dependency Injection for Agent Service
# =============================================================================

@lru_cache
def get_agent_service_cached(api_key: str, model_name: str) -> CreditRiskAgentService:
    """
    Create and cache the agent service instance.
    
    Using lru_cache with immutable parameters provides singleton-like behavior
    without mutable global state. The cache key is based on the parameters.
    """
    return CreditRiskAgentService(
        model_name=model_name,
        gemini_api_key=api_key,
    )


def get_agent_service(settings: Annotated[Settings, Depends(get_settings)]) -> CreditRiskAgentService:
    """
    Dependency injection function for the agent service.
    
    This is the proper FastAPI way to handle service dependencies:
    - No mutable global state
    - Easy to test (can override with different settings)
    - Thread-safe through caching
    """
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY environment variable not set. Service unavailable."
        )
    
    return get_agent_service_cached(
        api_key=settings.gemini_api_key,
        model_name=settings.gemini_model_name,
    )


# Type alias for cleaner endpoint signatures
AgentServiceDep = Annotated[CreditRiskAgentService, Depends(get_agent_service)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


# =============================================================================
# Pydantic Models
# =============================================================================

class ApplicantAnalysisRequest(BaseModel):
    """Request model for applicant analysis."""
    
    applicant_text: str = Field(
        ...,
        description="Raw text containing loan applicant information",
        min_length=10,
        examples=[
            """
            Applicant: John Doe
            Monthly Income: ₹75,000
            Existing EMIs: ₹15,000
            Loan Amount Requested: ₹20,00,000
            Property Value: ₹30,00,000
            Credit Score: 720
            Employment: Salaried, 5 years at current company
            Total Work Experience: 10 years
            Credit Card Limit: ₹2,00,000
            Credit Card Balance: ₹40,000
            """
        ]
    )


class ApplicantAnalysisResponse(BaseModel):
    """Response model for applicant analysis."""
    
    status: str = Field(..., description="Status of the analysis")
    response: str = Field(..., description="Risk assessment report")
    tools_used: list[str] = Field(default_factory=list, description="Tools used during analysis")
    message_count: int = Field(default=0, description="Number of messages in the conversation")


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str
    service: str
    model: str
    api_key_configured: bool


# =============================================================================
# FastAPI Application
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    settings = get_settings()
    
    if settings.gemini_api_key:
        print("✅ GEMINI_API_KEY configured")
        print(f"   Model: {settings.gemini_model_name}")
    else:
        print("⚠️ GEMINI_API_KEY not set. Set it in environment or .env file.")
    
    yield
    
    # Shutdown: Clear caches if needed
    get_settings.cache_clear()
    get_agent_service_cached.cache_clear()
    print("🛑 Shutting down Credit Risk Underwriting Assistant")


# Create FastAPI app
app = FastAPI(
    title="Credit Risk Underwriting Assistant",
    description="""
    GPT-based assistant that reviews loan applicant profiles and generates 
    comprehensive risk summary reports using LangChain and Google Gemini.
    
    ## Features
    - Analyzes raw text applicant profiles
    - Calculates multiple risk metrics (DTI, LTV, FOIR, etc.)
    - Provides risk classification and recommendations
    - Uses LangGraph ReAct agent pattern
    
    ## Usage
    Send applicant information as raw text to the `/analyze` endpoint.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for frontend
# Allow all origins since API Gateway also handles CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (API Gateway also configures CORS)
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/", response_model=HealthResponse)
async def root(settings: SettingsDep):
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        service="Credit Risk Underwriting Assistant",
        model=settings.gemini_model_name,
        api_key_configured=bool(settings.gemini_api_key),
    )


@app.get("/health", response_model=HealthResponse)
async def health_check(settings: SettingsDep):
    """Health check endpoint."""
    status = "ready" if settings.gemini_api_key else "waiting_for_api_key"
    
    return HealthResponse(
        status=status,
        service="Credit Risk Underwriting Assistant",
        model=settings.gemini_model_name,
        api_key_configured=bool(settings.gemini_api_key),
    )


@app.post("/analyze", response_model=ApplicantAnalysisResponse)
async def analyze_applicant(
    request: ApplicantAnalysisRequest,
    agent_service: AgentServiceDep,
):
    """
    Analyze a loan applicant profile and generate a risk assessment report.
    
    This endpoint accepts raw text containing applicant information and uses
    the Credit Risk Agent to:
    1. Extract relevant financial data
    2. Calculate risk metrics using specialized tools
    3. Classify the overall risk level
    4. Generate an underwriting recommendation
    
    **Example Input:**
    ```
    Applicant: John Doe
    Monthly Income: ₹75,000
    Existing EMIs: ₹15,000
    Loan Amount Requested: ₹20,00,000
    Property Value: ₹30,00,000
    Credit Score: 720
    Employment: Salaried, 5 years at current company
    ```
    """
    try:
        # Analyze the applicant using injected service
        result = agent_service.analyze_applicant(request.applicant_text)
        
        return ApplicantAnalysisResponse(
            status=result.get("status", "success"),
            response=result.get("response", ""),
            tools_used=result.get("tools_used", []),
            message_count=result.get("message_count", 0),
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing applicant: {str(e)}"
        )


@app.post("/analyze/stream")
async def analyze_applicant_stream(
    request: ApplicantAnalysisRequest,
    agent_service: AgentServiceDep,
):
    """
    Stream the analysis of a loan applicant profile.
    
    Returns a streaming response with chunks of the analysis as they are generated.
    Useful for real-time UI updates.
    """
    try:
        async def generate():
            for chunk in agent_service.analyze_applicant_stream(request.applicant_text):
                # Format chunk as Server-Sent Event
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing applicant: {str(e)}"
        )


# =============================================================================
# Run with Uvicorn
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
