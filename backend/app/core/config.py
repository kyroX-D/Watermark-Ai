from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Watermark System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # Gemini Vision API
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_FREE: str = "price_free"
    STRIPE_PRICE_PRO: str = "price_pro_id"
    STRIPE_PRICE_ELITE: str = "price_elite_id"

    # OxaPay
    OXAPAY_MERCHANT_ID: str
    OXAPAY_API_KEY: str
    OXAPAY_WEBHOOK_SECRET: str

    # Storage
    UPLOAD_DIR: str = "static/watermarks"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Subscription Limits
    FREE_DAILY_LIMIT: int = 2
    FREE_MAX_RESOLUTION: int = 720
    PRO_MAX_RESOLUTION: int = 1080
    ELITE_MAX_RESOLUTION: int = 2160  # 4K

    class Config:
        env_file = ".env"


settings = Settings()
