"""
Query Endpoint

This module provides endpoints for querying AI models, specifically
the Gemini AI API. Users can send questions or prompts and receive
AI-generated responses.

Endpoints:
    POST /query - Send a query to the AI and get a response
"""

import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas.query import QueryRequest, QueryResponse, ErrorResponse
from app.services.gemini_service import gemini_service

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