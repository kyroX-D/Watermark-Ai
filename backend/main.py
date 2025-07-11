# File: backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging

from app.api.endpoints import auth, users, watermarks, subscriptions, webhooks, admin
from app.core.config import settings
from app.core.database import engine, Base

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Watermark API",
    description="Intelligent watermarking system using AI",
    version="1.0.0"
)

# CORS configuration - Properly configured for production
origins = [
    "https://watermark-ai-frontend.onrender.com",
    "http://localhost:5173",
    "http://localhost:3000",
]

# Add CORS origins from environment if available
if hasattr(settings, 'CORS_ORIGINS'):
    if isinstance(settings.CORS_ORIGINS, list):
        origins.extend(settings.CORS_ORIGINS)
    elif isinstance(settings.CORS_ORIGINS, str):
        origins.append(settings.CORS_ORIGINS)

# Remove duplicates
origins = list(set(origins))

logger.info(f"CORS Origins configured: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Create directories if they don't exist
os.makedirs("static/watermarks", exist_ok=True)
os.makedirs("fonts", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(watermarks.router, prefix="/api/watermarks", tags=["watermarks"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root():
    return {
        "message": "AI Watermark API", 
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/api/auth",
            "users": "/api/users",
            "watermarks": "/api/watermarks"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }

# Log startup
@app.on_event("startup")
async def startup_event():
    logger.info("AI Watermark API started successfully")
    logger.info(f"CORS origins: {origins}")
    logger.info(f"Environment: {'production' if not settings.DEBUG else 'development'}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")