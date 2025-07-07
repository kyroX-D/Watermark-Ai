from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict

from ...core.database import get_db
from ...core.security import get_current_active_user, verify_password, get_password_hash
from ...models.user import User
from ...models.watermark import Watermark
from ...schemas.user import UserResponse, UserUpdate, PasswordChange, UserStats

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update user profile"""
    # Check if username is taken
    if user_update.username and user_update.username != current_user.username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")

    # Update fields
    if user_update.username:
        current_user.username = user_update.username

    # Only allow email update for non-OAuth users
    if user_update.email and not current_user.google_id:
        if user_update.email != current_user.email:
            if db.query(User).filter(User.email == user_update.email).first():
                raise HTTPException(status_code=400, detail="Email already registered")
            current_user.email = user_update.email

    db.commit()
    db.refresh(current_user)

    return UserResponse.from_orm(current_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change user password"""
    # Check if user has password (not OAuth)
    if current_user.google_id:
        raise HTTPException(
            status_code=400, detail="Password change not available for Google accounts"
        )

    # Verify current password
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=400, detail="New password must be at least 8 characters long"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get user statistics"""
    # Total watermarks
    total_watermarks = (
        db.query(func.count(Watermark.id))
        .filter(Watermark.user_id == current_user.id)
        .scalar()
    )

    # Today's watermarks
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_watermarks = (
        db.query(func.count(Watermark.id))
        .filter(
            Watermark.user_id == current_user.id, Watermark.created_at >= today_start
        )
        .scalar()
    )

    # Reset daily usage if needed
    if current_user.last_usage_reset.date() < datetime.utcnow().date():
        current_user.daily_usage = 0
        current_user.last_usage_reset = datetime.utcnow()
        db.commit()

    # Calculate remaining today for free tier
    remaining_today = None
    if current_user.subscription_tier == "free":
        remaining_today = max(0, 2 - current_user.daily_usage)

    return UserStats(
        total_images=total_watermarks,
        today_images=today_watermarks,
        remaining_today=remaining_today,
        subscription=current_user.subscription_tier,
    )


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Delete user account and all associated data"""
    # This will cascade delete all user's watermarks and payments
    db.delete(current_user)
    db.commit()

    return {"message": "Account deleted successfully"}
