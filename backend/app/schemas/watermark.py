# File: backend/app/schemas/watermark.py

from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
from datetime import datetime


class WatermarkCreate(BaseModel):
    watermark_text: str

    @field_validator("watermark_text")
    @classmethod
    def validate_watermark_text(cls, v: str) -> str:
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