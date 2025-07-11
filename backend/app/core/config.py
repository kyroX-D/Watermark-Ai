# backend/app/core/config.py

from pydantic_settings import BaseSettings
from typing import List, Optional
import json
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Watermark System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "default-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = ""

    # CORS
    CORS_ORIGINS: List[str] = []

    # Google OAuth (Optional)
    GOOGLE_CLIENT_ID: str = "dummy-client-id"
    GOOGLE_CLIENT_SECRET: str = "dummy-client-secret"
    GOOGLE_REDIRECT_URI: str = ""

    # Gemini Vision API (Optional)
    GEMINI_API_KEY: str = "dummy-api-key"
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Stripe (Optional)
    STRIPE_SECRET_KEY: str = "sk_test_dummy"
    STRIPE_WEBHOOK_SECRET: str = "whsec_dummy"
    STRIPE_PRICE_PRO: str = "price_dummy_pro"
    STRIPE_PRICE_ELITE: str = "price_dummy_elite"

    # OxaPay (Optional)
    OXAPAY_MERCHANT_ID: str = "dummy-merchant"
    OXAPAY_API_KEY: str = "dummy-api-key"
    OXAPAY_WEBHOOK_SECRET: str = "dummy-webhook-secret"

    # Storage
    UPLOAD_DIR: str = "static/watermarks"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024

    # Subscription Limits
    FREE_DAILY_LIMIT: int = 2
    FREE_MAX_RESOLUTION: int = 720
    PRO_MAX_RESOLUTION: int = 1080
    ELITE_MAX_RESOLUTION: int = 2160

    # URLs
    FRONTEND_URL: str = ""
    API_URL: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Parse CORS_ORIGINS from environment
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            try:
                # Try parsing as JSON array
                self.CORS_ORIGINS = json.loads(cors_env)
            except json.JSONDecodeError:
                # If not JSON, treat as comma-separated
                self.CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
        
        # Set default CORS origins if none provided
        if not self.CORS_ORIGINS:
            self.CORS_ORIGINS = [
                "https://watermark-ai-frontend.onrender.com",
                "http://localhost:5173",
                "http://localhost:3000"
            ]
        
        # Set URLs from environment or defaults
        if not self.FRONTEND_URL:
            self.FRONTEND_URL = os.getenv("FRONTEND_URL", "https://watermark-ai-frontend.onrender.com")
        
        if not self.API_URL:
            self.API_URL = os.getenv("API_URL", "https://watermark-backend-a4l8.onrender.com")
        
        if not self.GOOGLE_REDIRECT_URI:
            self.GOOGLE_REDIRECT_URI = f"{self.API_URL}/api/auth/google/callback"
        
        # Ensure DATABASE_URL is set
        if not self.DATABASE_URL:
            self.DATABASE_URL = os.getenv("DATABASE_URL", "")
            if not self.DATABASE_URL:
                raise ValueError("DATABASE_URL must be set")

settings = Settings()