"""
Query Schemas

Pydantic models for query-related API requests and responses.
These schemas define the structure and validation for data sent to
and received from the Gemini AI query endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class QueryRequest(BaseModel):
    """
    Schema for AI query requests.
    
    This defines the structure of data sent when making a query
    to the Gemini AI service.
    """
    
    query: str = Field(
        ...,
        description="The question or prompt to send to the AI",
        min_length=1,
        max_length=4000,
        example="What is the capital of France?"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Explain the concept of machine learning in simple terms"
            }
        }
    }


class UsageInfo(BaseModel):
    """
    Schema for API usage information.
    
    Contains token usage statistics for the AI response.
    """
    
    prompt_tokens: int = Field(
        description="Number of tokens in the input prompt",
        ge=0
    )
    completion_tokens: int = Field(
        description="Number of tokens in the generated response",
        ge=0
    )
    total_tokens: Optional[int] = Field(
        default=None,
        description="Total tokens used (prompt + completion)"
    )

    def model_post_init(self, __context) -> None:
        """Calculate total tokens after model initialization."""
        if self.total_tokens is None:
            self.total_tokens = self.prompt_tokens + self.completion_tokens


class QueryResponse(BaseModel):
    """
    Schema for AI query responses.
    
    This defines the structure of data returned from the Gemini AI service
    including the generated response and metadata.
    """
    
    response: str = Field(
        description="The AI-generated response to the query"
    )
    model: str = Field(
        description="The AI model used to generate the response",
        example="gemini-2.0-flash-exp"
    )
    usage: UsageInfo = Field(
        description="Token usage information for this request"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "response": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed for every task.",
                "model": "gemini-2.0-flash-exp",
                "usage": {
                    "prompt_tokens": 12,
                    "completion_tokens": 25,
                    "total_tokens": 37
                }
            }
        }
    }


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    
    Used when the query endpoint encounters an error.
    """
    
    error: str = Field(
        description="Error message describing what went wrong"
    )
    detail: Optional[str] = Field(
        default=None,
        description="Additional error details"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "API key not configured",
                "detail": "Gemini API key is required but not set in environment variables"
            }
        }
    }