"""
Credit Risk Underwriting Assistant - Agent Service
===================================================

This module provides the Credit Risk Agent service using LangGraph
with Google Gemini (Generative AI) as the LLM backend.
"""

import os
from typing import Optional, Generator, AsyncGenerator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from app.tools import CREDIT_RISK_TOOLS
from app.prompt import CREDIT_RISK_SYSTEM_PROMPT


class CreditRiskAgentService:
    """
    Service class for the Credit Risk Underwriting Agent.
    
    Uses LangGraph's ReAct agent pattern with Google Gemini for LLM
    and comprehensive credit risk assessment tools.
    """
    
    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        gemini_api_key: Optional[str] = None,
        temperature: float = 0,
    ):
        """
        Initialize the Credit Risk Agent.
        
        Args:
            model_name: Google Gemini model name (default: gemini-2.0-flash)
            gemini_api_key: Gemini API key (falls back to GEMINI_API_KEY env var)
            temperature: Model temperature for response generation (default: 0.1 for consistency)
        """
        self.model_name = model_name
        self.temperature = temperature
        
        # Get API key from argument or environment
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY environment variable "
                "or pass gemini_api_key parameter."
            )
        
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            convert_system_message_to_human=True,
        )
        
        # Create the agent with tools using new create_agent API
        self.agent = create_agent(
            model=self.llm,
            tools=CREDIT_RISK_TOOLS,
            system_prompt=CREDIT_RISK_SYSTEM_PROMPT,
        )
    
    def analyze_applicant(self, applicant_text: str) -> dict:
        """
        Analyze a loan applicant profile and generate a risk assessment.
        
        Args:
            applicant_text: Raw text containing applicant information
        
        Returns:
            Dictionary containing the agent's response and risk assessment
        """
        # Prepare the input message
        messages = [
            {
                "role": "user",
                "content": f"""Analyze the following loan applicant profile and generate a comprehensive risk assessment report:

---
{applicant_text}
---

Use the available tools to calculate all relevant risk metrics and provide your assessment."""
            }
        ]
        
        # Invoke the agent with increased recursion limit for complex analysis
        result = self.agent.invoke(
            {"messages": messages},
            config={"recursion_limit": 50}
        )
        
        return self._parse_result(result)
    
    def analyze_applicant_stream(self, applicant_text: str) -> Generator[str, None, None]:
        """
        Stream the analysis of a loan applicant profile.
        
        Args:
            applicant_text: Raw text containing applicant information
        
        Yields:
            Text chunks as they are generated (only final AI response, no tool outputs)
        """
        messages = [
            {
                "role": "user",
                "content": f"""Analyze the following loan applicant profile and generate a comprehensive risk assessment report:

---
{applicant_text}
---

Use the available tools to calculate all relevant risk metrics and provide your assessment."""
            }
        ]
        
        # Stream the agent response - only print final AI text (no tool outputs)
        # stream_mode="messages" returns (token, metadata) tuples
        for token, metadata in self.agent.stream(
            {"messages": messages},
            stream_mode="messages",
        ):
            # Only process output from the model node (skip tools node)
            if metadata.get('langgraph_node') != 'model':
                continue
            
            # Only yield text content, skip tool_call_chunk types
            if hasattr(token, 'content_blocks'):
                for block in token.content_blocks:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text = block.get('text', '')
                        if text:
                            yield text


    async def analyze_applicant_stream_async(self, applicant_text: str) -> AsyncGenerator[str, None]:
        """
        Stream the analysis of a loan applicant profile (async version).
        
        Args:
            applicant_text: Raw text containing applicant information
        
        Yields:
            Text chunks as they are generated
        """
        messages = [
            {
                "role": "user",
                "content": f"""Analyze the following loan applicant profile and generate a comprehensive risk assessment report:

---
{applicant_text}
---

Use the available tools to calculate all relevant risk metrics and provide your assessment."""
            }
        ]
        
        # Stream tokens using stream_mode="messages" 
        async for token, metadata in self.agent.astream(
            {"messages": messages},
            stream_mode="messages",
        ):
            # Only process output from the model node
            if metadata.get('langgraph_node') != 'model':
                continue
            
            if hasattr(token, 'content_blocks'):
                for block in token.content_blocks:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text = block.get('text', '')
                        if text:
                            yield text
    
    def _parse_result(self, result: dict) -> dict:
        """
        Parse the agent result into a structured response.
        
        Args:
            result: Raw result from the agent
        
        Returns:
            Structured response dictionary
        """
        messages = result.get("messages", [])
        
        # Get the final AI message
        final_response = ""
        tool_calls_made = []
        
        for message in messages:
            if hasattr(message, 'content'):
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_calls_made.extend([tc['name'] for tc in message.tool_calls])
                elif message.type == "ai" and message.content:
                    # Handle content as string or list of content blocks
                    content = message.content
                    if isinstance(content, str):
                        final_response = content
                    elif isinstance(content, list):
                        # Gemini returns [{'type': 'text', 'text': '...'}, ...]
                        text_parts = []
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                text_parts.append(block.get('text', ''))
                            elif isinstance(block, str):
                                text_parts.append(block)
                        final_response = ''.join(text_parts)
                    else:
                        final_response = str(content)
        
        return {
            "status": "success",
            "response": final_response,
            "tools_used": list(set(tool_calls_made)),
            "message_count": len(messages),
        }
