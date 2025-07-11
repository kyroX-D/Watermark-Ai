# File: backend/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os

from app.api.endpoints import auth, users, watermarks, subscriptions, webhooks, admin
from app.core.config import settings
from app.core.database import engine, Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Watermark API",
    description="Intelligent watermarking system using AI",
    version="1.0.0"
)

# Log CORS origins for debugging
logger.info(f"CORS Origins from settings: {settings.CORS_ORIGINS}")

# CORS configuration - TEMPORARILY allow all origins for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMPORARY - for debugging only!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Create static directory if it doesn't exist
os.makedirs("static/watermarks", exist_ok=True)

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
        "cors_origins": settings.CORS_ORIGINS,  # Debug info
        "environment": "production" if not settings.DEBUG else "development"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api_url": os.getenv("API_URL", "not set"),
        "frontend_url": os.getenv("FRONTEND_URL", "not set")
    }

# Debug endpoint to check CORS
@app.options("/api/auth/register")
async def options_register(request: Request):
    return JSONResponse(
        content={"message": "CORS preflight OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

# Catch-all for 404s
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error(f"404 Not Found: {request.url}")
    return JSONResponse(
        status_code=404,
        content={"detail": f"Not Found: {request.url}"}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)