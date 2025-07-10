# backend/app/schemas/admin.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class GrantSubscriptionRequest(BaseModel):
    """Request to grant subscription to a user"""
    email: str = Field(..., description="User email to grant subscription")
    tier: str = Field(..., description="Subscription tier (pro/elite)")
    duration_days: int = Field(..., ge=1, le=365, description="Duration in days")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for granting")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v
    
    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        if v not in ["pro", "elite"]:
            raise ValueError("Tier must be 'pro' or 'elite'")
        return v


class UserAdminView(BaseModel):
    """User data visible to admins"""
    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    subscription_tier: str
    subscription_end_date: Optional[datetime]
    daily_usage: int
    created_at: datetime
    watermarks_count: Optional[int] = 0
    payments_count: Optional[int] = 0
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdminStats(BaseModel):
    """System statistics for admin dashboard"""
    total_users: int
    free_users: int
    pro_users: int
    elite_users: int
    total_watermarks: int
    watermarks_today: int
    watermarks_this_week: int
    watermarks_this_month: int
    total_revenue: float
    revenue_this_month: float
    active_users_today: int
    active_users_this_week: int
    
    
class AdminActionLog(BaseModel):
    """Admin action log entry"""
    id: int
    admin_id: int
    admin_email: str
    action_type: str
    target_user_id: Optional[int]
    target_user_email: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class BulkUserUpdate(BaseModel):
    """Bulk update user subscriptions"""
    user_ids: List[int] = Field(..., min_items=1, max_items=100)
    tier: str = Field(..., description="Subscription tier to apply")
    duration_days: int = Field(..., ge=1, le=365)
    reason: str = Field(..., max_length=500)
    
    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        if v not in ["free", "pro", "elite"]:
            raise ValueError("Invalid tier")
        return v