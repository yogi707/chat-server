"""
Health Check Endpoint

This module provides a simple health check endpoint that can be used
for monitoring, load balancer health checks, and ensuring the API
is responding correctly.

Endpoints:
    GET /health - Returns basic health status information
"""

from fastapi import APIRouter
from typing import Dict, Any

# Create router for health-related endpoints
router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    This endpoint returns a simple status response to indicate that
    the API server is running and responding to requests. It can be
    used by load balancers, monitoring systems, or deployment tools
    to verify service availability.
    
    Returns:
        dict: Health status information including:
            - status: Current health status ("healthy")
            - message: Human-readable status message
    
    Example response:
        {
            "status": "healthy",
            "message": "API is running"
        }
    """
    return {
        "status": "healthy", 
        "message": "API is running"
    }