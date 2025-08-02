"""
FastAPI Chat Server Entry Point

This is the main entry point for the FastAPI chat server application.
It configures and starts the Uvicorn ASGI server with development settings.

Usage:
    python main.py

The server will start on http://0.0.0.0:8000 with auto-reload enabled for development.
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    # Start the FastAPI application using Uvicorn ASGI server
    uvicorn.run(
        "app.main:app",          # Application module and variable
        host="0.0.0.0",          # Listen on all network interfaces
        port=8000,               # Default development port
        reload=True,             # Auto-reload on code changes (development only)
        log_level="info"         # Set logging level
    )