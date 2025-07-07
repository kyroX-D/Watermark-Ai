from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
from datetime import datetime, timedelta

from ...core.database import get_db
from ...core.security import get_current_active_user
from ...core.config import settings
from ...models.user import User, SubscriptionTier
from ...models.watermark import Watermark
from ...schemas.watermark import WatermarkCreate, WatermarkResponse
from ...services.watermark_service import WatermarkService

router = APIRouter()


@router.post("/create", response_model=WatermarkResponse)
async def create_watermark(
    watermark_text: str = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new watermarked image"""

    # Check usage limits for free tier
    if current_user.subscription_tier == SubscriptionTier.FREE:
        # Reset daily usage if needed
        if current_user.last_usage_reset.date() < datetime.utcnow().date():
            current_user.daily_usage = 0
            current_user.last_usage_reset = datetime.utcnow()

        if current_user.daily_usage >= settings.FREE_DAILY_LIMIT:
            raise HTTPException(
                status_code=403,
                detail=f"Daily limit of {settings.FREE_DAILY_LIMIT} watermarks reached. Upgrade to Pro for unlimited watermarks.",
            )

    # Validate file
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if image.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # Read image
    image_bytes = await image.read()

    # Process watermark
    watermark_service = WatermarkService()
    start_time = datetime.utcnow()

    watermarked_bytes, ai_analysis = (
        await watermark_service.apply_intelligent_watermark(
            image_bytes, watermark_text, current_user.subscription_tier.value
        )
    )

    processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    # Save images
    file_id = str(uuid.uuid4())
    original_path = (
        f"{settings.UPLOAD_DIR}/{file_id}_original.{image.filename.split('.')[-1]}"
    )
    watermarked_path = f"{settings.UPLOAD_DIR}/{file_id}_watermarked.png"

    # Ensure directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Save original
    with open(original_path, "wb") as f:
        f.write(image_bytes)

    # Save watermarked
    with open(watermarked_path, "wb") as f:
        f.write(watermarked_bytes)

    # Save to database
    watermark = Watermark(
        user_id=current_user.id,
        original_image_url=f"/static/watermarks/{os.path.basename(original_path)}",
        watermarked_image_url=f"/static/watermarks/{os.path.basename(watermarked_path)}",
        watermark_text=watermark_text,
        ai_analysis=ai_analysis,
        placement_data=ai_analysis.get("placement_suggestions", [{}])[0],
        file_size=len(watermarked_bytes),
        processing_time=processing_time,
    )

    db.add(watermark)

    # Update usage
    current_user.daily_usage += 1

    db.commit()
    db.refresh(watermark)

    return WatermarkResponse.from_orm(watermark)


@router.get("/my-watermarks", response_model=List[WatermarkResponse])
async def get_my_watermarks(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get user's watermarked images"""
    watermarks = (
        db.query(Watermark)
        .filter(Watermark.user_id == current_user.id)
        .order_by(Watermark.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [WatermarkResponse.from_orm(w) for w in watermarks]


@router.delete("/{watermark_id}")
async def delete_watermark(
    watermark_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a watermarked image"""
    watermark = (
        db.query(Watermark)
        .filter(Watermark.id == watermark_id, Watermark.user_id == current_user.id)
        .first()
    )

    if not watermark:
        raise HTTPException(status_code=404, detail="Watermark not found")

    # Delete files
    for path in [watermark.original_image_url, watermark.watermarked_image_url]:
        file_path = os.path.join("static", path.lstrip("/static/"))
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(watermark)
    db.commit()

    return {"message": "Watermark deleted successfully"}
