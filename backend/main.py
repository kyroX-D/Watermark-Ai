# File: backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.endpoints import auth, users, watermarks, subscriptions, webhooks
from app.core.config import settings
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Watermark API",
    description="Intelligent watermarking system using AI",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(watermarks.router, prefix="/api/watermarks", tags=["watermarks"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "AI Watermark API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)