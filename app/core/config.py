from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Chat Server API"
    debug: bool = False
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    
    # Database
    database_url: Optional[str] = None
    
    # Redis
    redis_url: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080" , "http://localhost:5173"]
    
    # Gemini API
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash-exp"
    
    class Config:
        env_file = ".env.example"


settings = Settings()