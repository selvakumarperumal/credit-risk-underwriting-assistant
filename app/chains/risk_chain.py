# Import necessary modules and classes from LangChain, Pydantic, dotenv, and standard libraries
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAI,
    ChatGoogleGenerativeAIError
)
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json
from typing import Union, Optional, Sequence
from langchain_core.prompts.message import BaseMessagePromptTemplate
from pathlib import Path

# Load environment variables from the .env file located two directories up
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

# Retrieve the Gemini API key from environment variables
API_KEY = os.getenv("GEMINI_API")
if not API_KEY:
    raise ValueError("GEMINI_API key is not set in the environment variables.")

# Initialize the Gemini chat model with the API key and configuration
chat_model = ChatGoogleGenerativeAI(
    api_key=API_KEY,
    model="gemini-2.0-flash",         # Model name
    temperature=0.5,                  # Controls randomness of output
    max_output_tokens=1024,           # Max tokens in output
)

# Define a Pydantic model to validate and structure the risk assessment report
class RiskAssessmentReport(BaseModel):
    name: str
    age: int
    income: int
    credit_score: int
    loan_amount: int
    employment_status: str
    debt_to_income_ratio: float
    risk_level: Optional[str] = None
    recommendations: Optional[str] = None

# Create a system prompt that sets the assistant's role
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are a Credit Risk Underwriting Assistant. "
)

# Create a human prompt template that instructs the model to generate a JSON report
human_prompt = HumanMessagePromptTemplate.from_template(
    """Review the Loan Applicant Profile and generate a risk assessment report. Structure the report in JSON format. 
    Applicant Profile:
    {input}
    JSON Output Format:
    {{
      "name": "<name>",
      "age": <age>,
      "income": <income>,
      "credit_score": <credit_score>,
      "loan_amount": <loan_amount>,
      "employment_status": "<employment_status>",
      "debt_to_income_ratio": <debt_to_income_ratio>,
      "risk_level": "<risk_level>",
      "recommendations": "<recommendations>"
    }}
    Ensure the output is valid JSON and follows the specified format."""
)   

# Combine the system and human prompts into a chat prompt template
messages: Sequence[BaseMessagePromptTemplate] = [system_prompt, human_prompt]
chat_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(messages)

# Define an output parser that converts the model's JSON output into a Pydantic object
output_parser = JsonOutputParser(pydantic_object=RiskAssessmentReport)

# Create a runnable sequence (chain) that processes input through the prompt, model, and parser
# - chat_prompt: Formats the input using the system and human prompt templates.
# - chat_model: Sends the formatted prompt to the Gemini model for response generation.
# - output_parser: Parses the model's JSON output and validates it against the RiskAssessmentReport schema.
# The chain takes a dictionary input (with an "input" key for the applicant profile string)
# and outputs a validated RiskAssessmentReport object.
risk_assessment_chain: RunnableSequence[dict[str, str], RiskAssessmentReport] = RunnableSequence(
    chat_prompt | chat_model | output_parser
)

def assess_risk(applicant_profile: str) -> dict[str, object]:
    """
    Assess the risk of a loan applicant based on their profile.

    Args:
        applicant_profile (str): The profile of the loan applicant in text format.

    Returns:
        RiskAssessmentReport: A structured report containing the risk assessment.
    """
    try:
        # Run the risk assessment chain with the provided applicant profile
        result = risk_assessment_chain.invoke({"input": applicant_profile})
        return result 
    except ChatGoogleGenerativeAIError as e:
        # Handle errors from the chat model
        raise RuntimeError(f"Error during risk assessment: {e}") from e
    
def assess_risk_flexible(applicant_profile: Union[str, dict[str, object]]) -> dict[str, object]:
    """
    Assess risk, accepting either a string or a dict/JSON as input.

    Args:
        applicant_profile (Union[str, dict]): Applicant profile as string or dict.

    Returns:
        dict: Risk assessment report.
    """
    # If input is a dict, convert it to a JSON string; otherwise, use as string
    if isinstance(applicant_profile, dict):
        profile_str = json.dumps(applicant_profile)
    else:
        profile_str = str(applicant_profile)
    return assess_risk(profile_str)
    
# Example usage (uncomment to test):

# applicant_profile = """
# Name: Ravi Kumar  
# Age: 32  
# Credit Score: 615  
# Annual Income: ₹12,00,000  
# Employment Status: Full-time Software Engineer, 5 years experience  
# Existing Debts: ₹6,50,000 (Car Loan), ₹1,20,000 (Credit Card Balance)  
# Debt-to-Income Ratio: 64%  
# Loan Amount Requested: ₹15,00,000  
# Purpose of Loan: Home Renovation  
# Payment History: Occasional late credit card payments  
# Other Notes: No criminal record, married with one dependent child."""

# applicant_profile = """
# Name: John Doe
# Age: 30
# Income: 75000
# Credit Score: 720
# Loan Amount: 20000
# Employment Status: Employed
# Debt to Income Ratio: 0.25
# """

# report = assess_risk_flexible(applicant_profile)
# print(report)
# print(type(report))