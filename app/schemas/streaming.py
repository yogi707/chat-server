"""
Streaming Schemas

Pydantic models for streaming query-related API requests and responses.
These schemas define the structure for Server-Sent Events (SSE) streaming
responses from the AI service.
"""

from pydantic import BaseModel, Field
from typing import Optional


class StreamingChunk(BaseModel):
    """
    Schema for individual streaming response chunks.
    
    Each chunk represents a piece of the AI response as it's being generated.
    """
    
    text: str = Field(
        description="The text content of this chunk"
    )
    model: str = Field(
        description="The AI model generating the response",
        example="gemini-2.0-flash-exp"
    )
    done: bool = Field(
        description="Whether this is the final chunk in the stream",
        default=False
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if something went wrong"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "The capital of France",
                    "model": "gemini-2.0-flash-exp",
                    "done": False
                },
                {
                    "text": " is Paris.",
                    "model": "gemini-2.0-flash-exp", 
                    "done": False
                },
                {
                    "text": "",
                    "model": "gemini-2.0-flash-exp",
                    "done": True
                }
            ]
        }
    }


class StreamingQueryRequest(BaseModel):
    """
    Schema for streaming AI query requests.
    
    This defines the structure of data sent when making a streaming query
    to the Gemini AI service.
    """
    
    query: str = Field(
        ...,
        description="The question or prompt to send to the AI",
        min_length=1,
        max_length=4000,
        example="Explain quantum computing step by step"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Write a short story about a robot learning to paint"
            }
        }
    }