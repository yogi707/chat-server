"""
API v1 Router Configuration

This module aggregates all API v1 endpoint routers into a single router
that can be included in the main FastAPI application. This provides a
clean way to organize and version API endpoints.

All endpoints registered here will be available under the /api/v1 prefix.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, query

# Create the main API v1 router
api_router = APIRouter()

# Include endpoint routers with appropriate tags for OpenAPI documentation
api_router.include_router(
    health.router, 
    tags=["health"]  # Groups endpoints in OpenAPI/Swagger docs
)

api_router.include_router(
    query.router,
    tags=["ai-query"]  # Groups AI query endpoints in OpenAPI/Swagger docs
)

# Future endpoint routers can be added here:
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])