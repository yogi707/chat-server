"""
Schemas Package

Contains Pydantic models for request/response serialization and validation.
These schemas define the structure of data sent to and from the API endpoints.

Schemas are different from models:
- Models (SQLAlchemy): Define database structure and ORM relationships
- Schemas (Pydantic): Define API data validation and serialization

Future schemas might include:
- user.py: User creation, update, and response schemas
- message.py: Message creation and response schemas
- auth.py: Authentication request/response schemas

Example usage:
    from app.schemas.user import UserCreate, UserResponse
    from app.schemas.message import MessageCreate, MessageResponse
"""