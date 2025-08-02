"""
App Package

This package contains the main FastAPI application code organized into
logical modules:

- main.py: FastAPI application factory and configuration
- api/: API endpoints organized by version (v1, v2, etc.)
- core/: Core functionality like configuration, security, utilities
- models/: Database models (SQLAlchemy ORM models)
- schemas/: Pydantic models for request/response serialization
- services/: Business logic and service layer components
- utils/: Utility functions and helpers

The __init__.py files in Python packages serve two purposes:
1. Make directories into Python packages (importable modules)
2. Control what gets imported when someone does "from package import *"
"""