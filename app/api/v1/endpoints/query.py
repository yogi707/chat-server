"""
Query Endpoint

This module provides endpoints for querying AI models, specifically
the Gemini AI API. Users can send questions or prompts and receive
AI-generated responses in both regular and streaming formats.

Endpoints:
    POST /query - Send a query to the AI and get a complete response
    POST /query/stream - Send a query to the AI and get a streaming response
    GET /query/status - Check AI service status
"""

import json
import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from typing import AsyncGenerator

from app.schemas.query import QueryRequest, QueryResponse, ErrorResponse
from app.schemas.streaming import StreamingQueryRequest
from app.services.gemini_service import gemini_service
from app.services.conversation_store import conversation_store

logger = logging.getLogger(__name__)

# Create router for query-related endpoints
router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    },
    summary="Query AI Model",
    description="Send a query to the Gemini AI model and receive a generated response"
)
async def query_ai(request: QueryRequest) -> QueryResponse:
    """
    Query the Gemini AI model with a user prompt.
    
    This endpoint accepts a text query and forwards it to the Gemini AI service,
    returning the AI-generated response along with metadata about the request.
    
    Args:
        request (QueryRequest): The query request containing the user's prompt
        
    Returns:
        QueryResponse: The AI response with metadata including token usage
        
    Raises:
        HTTPException: Various HTTP errors for different failure scenarios
        
    Example:
        ```json
        POST /api/v1/query
        {
            "query": "What is the capital of France?"
        }
        
        Response:
        {
            "response": "The capital of France is Paris.",
            "model": "gemini-2.0-flash-exp",
            "usage": {
                "prompt_tokens": 8,
                "completion_tokens": 8,
                "total_tokens": 16
            }
        }
        ```
    """
    try:
        logger.info(f"Received query request: {request.query[:100]}...")
        
        # Check if Gemini service is configured
        if not gemini_service.is_configured():
            logger.error("Gemini service not configured")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is not configured. Please check API key settings."
            )
        
        # Validate query length (additional validation beyond Pydantic)
        if len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        # Generate response using Gemini service
        try:
            result = await gemini_service.generate_response(request.query)
            
            # Create response object
            response = QueryResponse(
                response=result["response"],
                model=result["model"],
                usage=result["usage"]
            )
            
            logger.info("Successfully generated AI response")
            return response
            
        except ValueError as ve:
            logger.error(f"Configuration error: {str(ve)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service configuration error: {str(ve)}"
            )
        
        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate AI response: {str(e)}"
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in query endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request"
        )


@router.get(
    "/query/status",
    summary="Check AI Service Status",
    description="Check if the AI service is configured and available"
)
async def query_service_status():
    """
    Check the status of the AI query service.
    
    This endpoint provides information about whether the Gemini AI service
    is properly configured and ready to accept queries.
    
    Returns:
        dict: Service status information
        
    Example:
        ```json
        GET /api/v1/query/status
        
        Response:
        {
            "status": "available",
            "configured": true,
            "model": "gemini-2.0-flash-exp"
        }
        ```
    """
    try:
        is_configured = gemini_service.is_configured()
        
        return {
            "status": "available" if is_configured else "unavailable",
            "configured": is_configured,
            "model": gemini_service.model_name if is_configured else None,
            "message": "AI service is ready" if is_configured else "AI service requires configuration"
        }
        
    except Exception as e:
        logger.error(f"Error checking service status: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "configured": False,
                "model": None,
                "message": f"Error checking service status: {str(e)}"
            }
        )


@router.post(
    "/query/stream",
    responses={
        200: {"description": "Streaming response", "content": {"text/plain": {}}},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    },
    summary="Stream AI Query Response",
    description="Send a query to the Gemini AI model and receive a streaming response via Server-Sent Events"
)
async def stream_query_ai(request: StreamingQueryRequest) -> StreamingResponse:
    """
    Stream the Gemini AI model response with a user prompt.
    
    This endpoint accepts a text query and streams the AI-generated response
    in real-time using Server-Sent Events (SSE). The client receives chunks
    of the response as they're generated by the AI model.
    
    Args:
        request (StreamingQueryRequest): The query request containing the user's prompt
        
    Returns:
        StreamingResponse: Server-Sent Events stream of AI response chunks
        
    Raises:
        HTTPException: Various HTTP errors for different failure scenarios
        
    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/query/stream" \
             -H "Content-Type: application/json" \
             -d '{"query": "Tell me a short story"}' \
             --no-buffer
        
        # Response (Server-Sent Events):
        data: {"text": "Once upon a time", "model": "gemini-2.0-flash-exp", "done": false}
        
        data: {"text": ", in a small village", "model": "gemini-2.0-flash-exp", "done": false}
        
        data: {"text": "", "model": "gemini-2.0-flash-exp", "done": true}
        ```
    """
    
    # Validation checks (similar to regular query endpoint)
    if not gemini_service.is_configured():
        logger.error("Gemini service not configured for streaming")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured. Please check API key settings."
        )
    
    if len(request.query.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    return StreamingResponse(
        gemini_service.generate_stream(request.query, request.conversation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",  # Allow CORS for streaming
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )


@router.get(
    "/conversation/{conversation_id}",
    summary="Get Conversation History",
    description="Retrieve the conversation history for a given conversation ID"
)
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history by conversation ID.
    
    Args:
        conversation_id: The ID of the conversation to retrieve
        
    Returns:
        dict: Conversation history with messages and metadata
    """
    try:
        conversation = conversation_store.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        return {
            "conversation_id": conversation.conversation_id,
            "created_at": conversation.created_at.isoformat(),
            "last_accessed": conversation.last_accessed.isoformat(),
            "message_count": conversation.message_count(),
            "messages": [
                {
                    "query": msg.query,
                    "response": msg.response,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                }
                for msg in conversation.messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history"
        )


@router.get(
    "/conversations/stats",
    summary="Get Conversation Store Statistics",
    description="Get statistics about the conversation store"
)
async def get_conversation_stats():
    """
    Get conversation store statistics.
    
    Returns:
        dict: Statistics about active conversations and store health
    """
    try:
        return conversation_store.get_stats()
    except Exception as e:
        logger.error(f"Error getting conversation stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation statistics"
        )