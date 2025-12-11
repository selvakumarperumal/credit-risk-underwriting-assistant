"""
AWS Lambda handler for Credit Risk Underwriting Assistant.

This module adapts the FastAPI application for AWS Lambda using Mangum.
"""
import json
import logging
import os
from typing import Any

import boto3
from mangum import Mangum

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def load_secrets() -> dict[str, Any]:
    """
    Load secrets from AWS Secrets Manager.
    
    Returns:
        Dictionary of secret key-value pairs
    """
    secrets_arn = os.environ.get("SECRETS_ARN")
    if not secrets_arn:
        logger.warning("SECRETS_ARN not set, using environment variables directly")
        return {}
    
    try:
        region = os.environ.get("AWS_REGION_CUSTOM", "ap-south-1")
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secrets_arn)
        return json.loads(response["SecretString"])
    except Exception as e:
        logger.error(f"Failed to load secrets: {e}")
        return {}


def initialize_environment() -> None:
    """
    Initialize environment variables from AWS Secrets Manager.
    
    This sets GEMINI_API_KEY and GEMINI_MODEL_NAME before the app loads.
    """
    secrets = load_secrets()
    
    # Set Gemini API key
    if "GEMINI_API_KEY" in secrets:
        os.environ["GEMINI_API_KEY"] = secrets["GEMINI_API_KEY"]
    
    # Set Gemini model name
    if "GEMINI_MODEL_NAME" in secrets:
        os.environ["GEMINI_MODEL_NAME"] = secrets["GEMINI_MODEL_NAME"]


# Initialize environment before importing the app
initialize_environment()

# Now import the FastAPI app (after environment is set up)
from app.main import app  # noqa: E402

# Create the Lambda handler
handler = Mangum(app, lifespan="off")
