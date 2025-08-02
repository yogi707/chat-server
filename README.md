# Chat Server API

A FastAPI-based chat server with WebSocket support, designed for real-time messaging applications.

## Project Structure

```
chat-server/
├── venv/                    # Python virtual environment
├── app/                     # Main application package
│   ├── main.py             # FastAPI app factory and configuration
│   ├── api/                # API endpoints organized by version
│   │   └── v1/             # Version 1 API endpoints
│   │       ├── api.py      # Main v1 router aggregator
│   │       └── endpoints/  # Individual endpoint modules
│   │           └── health.py   # Health check endpoints
│   ├── core/               # Core application functionality
│   │   └── config.py       # Application settings and configuration
│   ├── models/             # SQLAlchemy database models
│   ├── schemas/            # Pydantic models for API serialization
│   ├── services/           # Business logic and service layer
│   └── utils/              # Utility functions and helpers
├── tests/                  # Test files
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **CORS Support**: Configured for frontend integration
- **Environment Configuration**: Flexible settings management with Pydantic
- **Health Check Endpoint**: Built-in monitoring and health verification
- **Modular Architecture**: Clean separation of concerns with organized package structure
- **Type Safety**: Full type hints and validation with Pydantic

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd chat-server
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your specific configuration
```

### 5. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## Configuration

The application uses environment variables for configuration. Key settings include:

- `APP_NAME`: Application name (default: "Chat Server API")
- `DEBUG`: Enable debug mode (default: False)
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Secret key for security features
- `ALLOWED_ORIGINS`: CORS allowed origins

See `.env.example` for all available configuration options.

## Development

### Adding New Endpoints

1. Create a new module in `app/api/v1/endpoints/`
2. Define your FastAPI router and endpoints
3. Add the router to `app/api/v1/api.py`

Example:
```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
async def list_users():
    return {"users": []}

# app/api/v1/api.py
from app.api.v1.endpoints import users
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

### Project Architecture

- **app/main.py**: FastAPI application factory with middleware and router configuration
- **app/api/**: API endpoints organized by version for backward compatibility
- **app/core/**: Core functionality like configuration, security, and database setup
- **app/models/**: SQLAlchemy ORM models for database entities
- **app/schemas/**: Pydantic models for request/response validation
- **app/services/**: Business logic and complex operations
- **app/utils/**: Utility functions and helpers

### Understanding `__init__.py` Files

The `__init__.py` files serve two important purposes:

1. **Package Definition**: They make directories into Python packages that can be imported
2. **Import Control**: They control what gets exposed when someone imports the package

Each `__init__.py` file in this project contains documentation explaining the purpose of that package and what modules it contains or will contain in the future.

## Testing

```bash
# Run tests (when test files are added)
pytest

# Run with coverage
pytest --cov=app
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment variables
2. Use a production ASGI server like Gunicorn with Uvicorn workers
3. Configure a reverse proxy (nginx)
4. Set up proper database and Redis instances
5. Configure logging and monitoring

## Dependencies

Key dependencies include:

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and settings
- **SQLAlchemy**: Database ORM
- **Alembic**: Database migrations
- **Redis**: Caching and session storage
- **Celery**: Background task processing

See `requirements.txt` for complete dependency list.

## License

[Add your license information here]