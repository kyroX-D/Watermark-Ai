# backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import json

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Watermark System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False  # Changed to False for production

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str

    # CORS - Parse JSON string
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Google OAuth
    GOOGLE_CLIENT_ID: str = "dummy-client-id"
    GOOGLE_CLIENT_SECRET: str = "dummy-client-secret"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # Gemini Vision API
    GEMINI_API_KEY: str = "dummy-api-key"
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Stripe
    STRIPE_SECRET_KEY: str = "sk_test_dummy"
    STRIPE_WEBHOOK_SECRET: str = "whsec_dummy"
    STRIPE_PRICE_PRO: str = "price_dummy_pro"
    STRIPE_PRICE_ELITE: str = "price_dummy_elite"

    # OxaPay
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
    FRONTEND_URL: str = "http://localhost:5173"
    API_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS if it's a JSON string
        if isinstance(self.CORS_ORIGINS, str):
            try:
                self.CORS_ORIGINS = json.loads(self.CORS_ORIGINS)
            except:
                self.CORS_ORIGINS = [self.CORS_ORIGINS]

settings = Settings()