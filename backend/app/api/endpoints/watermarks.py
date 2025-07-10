# File: backend/app/api/endpoints/watermarks.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import uuid
import os
from datetime import datetime, timedelta
from pathlib import Path

from ...core.database import get_db
from ...core.security import get_current_active_user
from ...core.config import settings
from ...models.user import User, SubscriptionTier
from ...models.watermark import Watermark
from ...schemas.watermark import WatermarkCreate, WatermarkResponse
from ...services.watermark_service import WatermarkService
from ...utils.validators import validate_image_file, sanitize_watermark_text

router = APIRouter()


def secure_filename(filename: str) -> str:
    """Generate a secure filename"""
    # Get file extension
    ext = filename.split('.')[-1] if '.' in filename else 'png'
    # Only allow alphanumeric extensions
    ext = ''.join(c for c in ext if c.isalnum()).lower()
    # Limit extension length
    ext = ext[:10]
    # Validate against allowed extensions
    allowed_exts = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if ext not in allowed_exts:
        ext = 'png'
    return ext


@router.post("/create", response_model=WatermarkResponse)
async def create_watermark(
    watermark_text: str = Form(...),
    image: UploadFile = File(...),
    # Position parameters
    text_position: str = Form("bottom-right"),
    # Size and opacity
    text_size: str = Form("medium"),
    text_opacity: float = Form(0.7),
    auto_opacity: bool = Form(False),
    # Multiple watermarks
    multiple_watermarks: bool = Form(False),
    watermark_pattern: str = Form("diagonal"),
    # Font and styling
    font_family: Optional[str] = Form(None),
    text_color: str = Form("#FFFFFF"),
    text_shadow: bool = Form(False),
    # Protection mode
    protection_mode: str = Form("standard"),
    # User dependency
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new watermarked image with enhanced AI protection"""
    
    # Validate and sanitize watermark text
    watermark_text = sanitize_watermark_text(watermark_text)
    if not watermark_text:
        raise HTTPException(status_code=400, detail="Watermark text cannot be empty")
    
    if len(watermark_text) > 100:
        raise HTTPException(status_code=400, detail="Watermark text must be 100 characters or less")
    
    # Validate position
    valid_positions = [
        "top-left", "top-center", "top-right",
        "left-center", "center", "right-center",
        "bottom-left", "bottom-center", "bottom-right",
        "auto"  # AI-selected position
    ]
    if text_position not in valid_positions:
        raise HTTPException(status_code=400, detail=f"Invalid position. Must be one of: {valid_positions}")
    
    # Validate size
    valid_sizes = ["small", "medium", "large"]
    if text_size not in valid_sizes:
        raise HTTPException(status_code=400, detail=f"Invalid size. Must be one of: {valid_sizes}")
    
    # Validate opacity
    if not auto_opacity and not 0.1 <= text_opacity <= 1.0:
        raise HTTPException(status_code=400, detail="Opacity must be between 0.1 and 1.0")
    
    # Validate pattern
    valid_patterns = ["diagonal", "grid", "random"]
    if multiple_watermarks and watermark_pattern not in valid_patterns:
        raise HTTPException(status_code=400, detail=f"Invalid pattern. Must be one of: {valid_patterns}")
    
    # Validate protection mode
    valid_protection_modes = ["standard", "contextual", "multilayer"]
    if protection_mode not in valid_protection_modes:
        raise HTTPException(status_code=400, detail=f"Invalid protection mode. Must be one of: {valid_protection_modes}")
    
    # Check if advanced features require higher tier
    if protection_mode == "multilayer" and current_user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=403,
            detail="Multilayer protection is available for Pro and Elite users only"
        )
    
    if text_position == "auto" and current_user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=403,
            detail="AI-powered auto positioning is available for Pro and Elite users only"
        )
    
    # Validate color format
    if not text_color.startswith("#") or len(text_color) != 7:
        raise HTTPException(status_code=400, detail="Color must be in hex format (e.g., #FFFFFF)")
    
    # Additional hex color validation
    try:
        int(text_color[1:], 16)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid hex color format")

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
    validate_image_file(image)

    # Read image
    image_bytes = await image.read()

    # Process watermark with enhanced features
    watermark_service = WatermarkService()
    start_time = datetime.utcnow()

    try:
        watermarked_bytes, ai_analysis = (
            await watermark_service.apply_intelligent_watermark(
                image_bytes, 
                watermark_text, 
                current_user.subscription_tier.value,
                text_position=text_position,
                text_size=text_size,
                text_opacity=text_opacity,
                auto_opacity=auto_opacity,
                multiple_watermarks=multiple_watermarks,
                watermark_pattern=watermark_pattern,
                font_family=font_family if current_user.subscription_tier.value in ["pro", "elite"] else None,
                text_color=text_color if current_user.subscription_tier.value in ["pro", "elite"] else "#FFFFFF",
                text_shadow=text_shadow and current_user.subscription_tier.value == "elite",
                protection_mode=protection_mode
            )
        )
    except Exception as e:
        print(f"Watermark processing error: {e}")
        raise HTTPException(status_code=500, detail="Error processing watermark")

    processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    # Generate secure filenames
    file_id = str(uuid.uuid4())
    original_ext = secure_filename(image.filename)
    
    # Create safe paths
    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    os.makedirs(upload_dir, exist_ok=True)
    
    original_filename = f"{file_id}_original.{original_ext}"
    watermarked_filename = f"{file_id}_watermarked.png"
    
    original_path = upload_dir / original_filename
    watermarked_path = upload_dir / watermarked_filename
    
    # Verify paths are within upload directory
    if not str(original_path).startswith(str(upload_dir)) or not str(watermarked_path).startswith(str(upload_dir)):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # Save images
    try:
        # Save original
        with open(original_path, "wb") as f:
            f.write(image_bytes)

        # Save watermarked
        with open(watermarked_path, "wb") as f:
            f.write(watermarked_bytes)
    except Exception as e:
        print(f"Error saving files: {e}")
        raise HTTPException(status_code=500, detail="Error saving watermarked image")

    # Save to database
    watermark = Watermark(
        user_id=current_user.id,
        original_image_url=f"/static/watermarks/{original_filename}",
        watermarked_image_url=f"/static/watermarks/{watermarked_filename}",
        watermark_text=watermark_text,
        ai_analysis=ai_analysis,
        placement_data={
            "position": text_position,
            "size": text_size,
            "opacity": text_opacity,
            "auto_opacity": auto_opacity,
            "multiple": multiple_watermarks,
            "pattern": watermark_pattern if multiple_watermarks else None,
            "color": text_color,
            "font": font_family,
            "shadow": text_shadow,
            "protection_mode": protection_mode
        },
        file_size=len(watermarked_bytes),
        processing_time=processing_time,
    )

    db.add(watermark)

    # Update usage
    current_user.daily_usage += 1

    db.commit()
    db.refresh(watermark)

    return WatermarkResponse.model_validate(watermark)


@router.get("/my-watermarks", response_model=List[WatermarkResponse])
async def get_my_watermarks(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get user's watermarked images"""
    # Validate pagination
    if skip < 0:
        skip = 0
    if limit < 1 or limit > 100:
        limit = 20
        
    watermarks = (
        db.query(Watermark)
        .filter(Watermark.user_id == current_user.id)
        .order_by(Watermark.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [WatermarkResponse.model_validate(w) for w in watermarks]


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

    # Create safe paths for deletion
    upload_dir = Path(settings.UPLOAD_DIR).resolve()
    
    # Delete files safely
    for url in [watermark.original_image_url, watermark.watermarked_image_url]:
        if url.startswith("/static/watermarks/"):
            filename = url.replace("/static/watermarks/", "")
            # Sanitize filename
            filename = os.path.basename(filename)
            file_path = upload_dir / filename
            
            # Verify path is within upload directory
            if str(file_path).startswith(str(upload_dir)) and file_path.exists():
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

    db.delete(watermark)
    db.commit()

    return {"message": "Watermark deleted successfully"}


@router.get("/fonts", response_model=List[Dict[str, str]])
async def get_available_fonts(
    current_user: User = Depends(get_current_active_user),
):
    """Get list of available fonts based on user tier"""
    
    base_fonts = ["Arial", "Open Sans"]
    pro_fonts = ["Roboto", "Lato", "Montserrat", "Poppins"]
    elite_fonts = ["Inter", "Playfair Display", "Times New Roman", "Georgia", "Verdana", "Courier New"]
    
    available_fonts = []
    
    # Add base fonts (available to all)
    for font in base_fonts:
        available_fonts.append({
            "name": font,
            "tier": "free",
            "available": "true"
        })
    
    # Add pro fonts
    for font in pro_fonts:
        available_fonts.append({
            "name": font,
            "tier": "pro",
            "available": "true" if current_user.subscription_tier.value in ["pro", "elite"] else "false"
        })
    
    # Add elite fonts
    for font in elite_fonts:
        available_fonts.append({
            "name": font,
            "tier": "elite",
            "available": "true" if current_user.subscription_tier.value == "elite" else "false"
        })
    
    return available_fonts