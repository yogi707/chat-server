"""
FastAPI Application Factory

This module contains the FastAPI application factory function that creates
and configures the main FastAPI application instance with all necessary
middleware, routers, and settings.

The application factory pattern allows for easy testing and configuration
of different application instances.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router


def create_application() -> FastAPI:
    """
    Create and configure a FastAPI application instance.
    
    This factory function:
    1. Creates a FastAPI app with metadata from settings
    2. Configures CORS middleware for cross-origin requests
    3. Includes API routers with versioned prefixes
    
    Returns:
        FastAPI: Configured application instance
    """
    # Create FastAPI application with metadata from settings
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        debug=settings.debug,
        description="A FastAPI-based chat server with WebSocket support"
    )
    
    # Configure CORS middleware to allow frontend connections
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,    # Frontend URLs
        allow_credentials=True,                    # Allow cookies/auth
        allow_methods=["*"],                       # All HTTP methods
        allow_headers=["*"],                       # All headers
    )
    
    # Include versioned API routes under /api/v1 prefix
    app.include_router(api_router, prefix=settings.api_v1_str)
    
    return app


# Create the main application instance
app = create_application()