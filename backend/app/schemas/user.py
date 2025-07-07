from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from ..models.user import SubscriptionTier


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @validator("new_password")
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    subscription_tier: SubscriptionTier
    subscription_end_date: Optional[datetime]
    created_at: datetime
    google_id: Optional[str]
    daily_usage: int

    class Config:
        orm_mode = True
        from_attributes = True


class UserStats(BaseModel):
    total_images: int
    today_images: int
    remaining_today: Optional[int]
    subscription: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# File: backend/app/schemas/watermark.py

from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from datetime import datetime


class WatermarkCreate(BaseModel):
    watermark_text: str

    @validator("watermark_text")
    def validate_watermark_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Watermark text cannot be empty")
        if len(v) > 50:
            raise ValueError("Watermark text must be 50 characters or less")
        return v.strip()


class WatermarkResponse(BaseModel):
    id: int
    user_id: int
    original_image_url: str
    watermarked_image_url: str
    watermark_text: str
    ai_analysis: Optional[Dict[str, Any]]
    placement_data: Optional[Dict[str, Any]]
    image_width: Optional[int]
    image_height: Optional[int]
    file_size: Optional[int]
    processing_time: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
