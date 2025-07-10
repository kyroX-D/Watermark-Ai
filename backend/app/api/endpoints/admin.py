# backend/app/api/endpoints/admin.py

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import logging

from ...core.database import get_db
from ...core.security import get_current_active_user
from ...core.config import settings
from ...models.user import User, SubscriptionTier
from ...models.watermark import Watermark
from ...models.payment import Payment, PaymentStatus
from ...models.admin import AdminAction
from ...schemas.admin import (
    UserAdminView, 
    AdminStats, 
    GrantSubscriptionRequest,
    AdminActionLog,
    BulkUserUpdate
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Hardcoded admin email for ultimate security
SUPER_ADMIN_EMAIL = "bidar.qadir@gmail.com"  # CHANGE THIS TO YOUR EMAIL


def get_admin_user(
    current_user: User = Depends(get_current_active_user),
    request: Request = None
) -> User:
    """
    Verify user is admin with multiple security checks
    """
    # Check 1: User must be authenticated
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Check 2: User must have admin flag
    if not current_user.is_admin:
        # Log unauthorized access attempt
        logger.warning(
            f"Unauthorized admin access attempt by user {current_user.email} (ID: {current_user.id})"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check 3: For critical operations, verify against hardcoded email
    if current_user.email != SUPER_ADMIN_EMAIL:
        logger.warning(
            f"Admin access by non-super admin: {current_user.email}"
        )
    
    return current_user


def log_admin_action(
    db: Session,
    admin: User,
    action_type: str,
    target_user_id: Optional[int] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None
):
    """Log admin action for audit trail"""
    action = AdminAction(
        admin_id=admin.id,
        action_type=action_type,
        target_user_id=target_user_id,
        details=details,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    db.add(action)
    db.commit()


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system statistics - Read only, safe operation"""
    try:
        # User statistics
        total_users = db.query(User).count()
        free_users = db.query(User).filter(User.subscription_tier == SubscriptionTier.FREE).count()
        pro_users = db.query(User).filter(User.subscription_tier == SubscriptionTier.PRO).count()
        elite_users = db.query(User).filter(User.subscription_tier == SubscriptionTier.ELITE).count()
        
        # Watermark statistics
        total_watermarks = db.query(Watermark).count()
        
        today = datetime.utcnow().date()
        watermarks_today = db.query(Watermark).filter(
            func.date(Watermark.created_at) == today
        ).count()
        
        week_ago = today - timedelta(days=7)
        watermarks_this_week = db.query(Watermark).filter(
            Watermark.created_at >= week_ago
        ).count()
        
        month_ago = today - timedelta(days=30)
        watermarks_this_month = db.query(Watermark).filter(
            Watermark.created_at >= month_ago
        ).count()
        
        # Revenue statistics (completed payments only)
        total_revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.payment_status == PaymentStatus.COMPLETED
        ).scalar() or 0
        
        revenue_this_month = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.payment_status == PaymentStatus.COMPLETED,
                Payment.completed_at >= month_ago
            )
        ).scalar() or 0
        
        # Active users
        active_users_today = db.query(func.count(func.distinct(Watermark.user_id))).filter(
            func.date(Watermark.created_at) == today
        ).scalar() or 0
        
        active_users_this_week = db.query(func.count(func.distinct(Watermark.user_id))).filter(
            Watermark.created_at >= week_ago
        ).scalar() or 0
        
        return AdminStats(
            total_users=total_users,
            free_users=free_users,
            pro_users=pro_users,
            elite_users=elite_users,
            total_watermarks=total_watermarks,
            watermarks_today=watermarks_today,
            watermarks_this_week=watermarks_this_week,
            watermarks_this_month=watermarks_this_month,
            total_revenue=float(total_revenue),
            revenue_this_month=float(revenue_this_month),
            active_users_today=active_users_today,
            active_users_this_week=active_users_this_week
        )
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.get("/users", response_model=List[UserAdminView])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),  # Max 100 to prevent DOS
    search: Optional[str] = Query(None, max_length=100),
    subscription_tier: Optional[str] = Query(None),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List users with pagination and filtering"""
    try:
        query = db.query(User)
        
        # Apply search filter
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_term),
                    User.username.ilike(search_term)
                )
            )
        
        # Apply subscription filter
        if subscription_tier:
            if subscription_tier in ["free", "pro", "elite"]:
                query = query.filter(User.subscription_tier == subscription_tier)
        
        # Get users with counts
        users = query.offset(skip).limit(limit).all()
        
        # Add watermark and payment counts
        result = []
        for user in users:
            user_dict = UserAdminView.model_validate(user).model_dump()
            user_dict["watermarks_count"] = db.query(Watermark).filter(
                Watermark.user_id == user.id
            ).count()
            user_dict["payments_count"] = db.query(Payment).filter(
                Payment.user_id == user.id
            ).count()
            result.append(UserAdminView(**user_dict))
        
        return result
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.post("/grant-subscription")
async def grant_subscription(
    request: GrantSubscriptionRequest,
    admin_user: User = Depends(get_admin_user),
    req: Request = None,
    db: Session = Depends(get_db)
):
    """
    Grant free subscription to user - High security operation
    """
    # Additional security check for critical operation
    if admin_user.email != SUPER_ADMIN_EMAIL:
        # Log non-super admin grant attempt
        logger.warning(
            f"Non-super admin {admin_user.email} attempted to grant subscription"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can grant subscriptions"
        )
    
    # Validate target user exists
    target_user = db.query(User).filter(User.email == request.email).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {request.email} not found"
        )
    
    # Prevent self-granting (defense in depth)
    if target_user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot grant subscription to yourself"
        )
    
    try:
        # Update user subscription
        old_tier = target_user.subscription_tier
        old_end_date = target_user.subscription_end_date
        
        target_user.subscription_tier = SubscriptionTier(request.tier)
        target_user.subscription_end_date = datetime.utcnow() + timedelta(days=request.duration_days)
        
        # Log the action with full details
        log_admin_action(
            db=db,
            admin=admin_user,
            action_type="grant_subscription",
            target_user_id=target_user.id,
            details={
                "old_tier": old_tier.value if old_tier else None,
                "new_tier": request.tier,
                "old_end_date": old_end_date.isoformat() if old_end_date else None,
                "new_end_date": target_user.subscription_end_date.isoformat(),
                "duration_days": request.duration_days,
                "reason": request.reason,
                "granted_by_email": admin_user.email
            },
            request=req
        )
        
        db.commit()
        
        # Log success
        logger.info(
            f"Admin {admin_user.email} granted {request.tier} subscription to {target_user.email} "
            f"for {request.duration_days} days. Reason: {request.reason}"
        )
        
        return {
            "success": True,
            "message": f"Successfully granted {request.tier} subscription to {target_user.email}",
            "details": {
                "user_id": target_user.id,
                "email": target_user.email,
                "tier": request.tier,
                "expires_at": target_user.subscription_end_date.isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error granting subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant subscription"
        )


@router.get("/users/{user_id}", response_model=UserAdminView)
async def get_user_details(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Add counts
    user_data = UserAdminView.model_validate(user).model_dump()
    user_data["watermarks_count"] = db.query(Watermark).filter(
        Watermark.user_id == user.id
    ).count()
    user_data["payments_count"] = db.query(Payment).filter(
        Payment.user_id == user.id
    ).count()
    
    return UserAdminView(**user_data)


@router.get("/logs", response_model=List[AdminActionLog])
async def get_admin_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action_type: Optional[str] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin action logs for auditing"""
    # Only super admin can view logs
    if admin_user.email != SUPER_ADMIN_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can view logs"
        )
    
    query = db.query(AdminAction)
    
    if action_type:
        query = query.filter(AdminAction.action_type == action_type)
    
    logs = query.order_by(AdminAction.created_at.desc()).offset(skip).limit(limit).all()
    
    # Format logs with user emails
    result = []
    for log in logs:
        log_data = {
            "id": log.id,
            "admin_id": log.admin_id,
            "admin_email": log.admin.email if log.admin else "Unknown",
            "action_type": log.action_type,
            "target_user_id": log.target_user_id,
            "target_user_email": log.target_user.email if log.target_user else None,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at
        }
        result.append(AdminActionLog(**log_data))
    
    return result


@router.delete("/users/{user_id}/subscription")
async def revoke_subscription(
    user_id: int,
    reason: str = Query(..., max_length=500),
    admin_user: User = Depends(get_admin_user),
    req: Request = None,
    db: Session = Depends(get_db)
):
    """Revoke user subscription - Super admin only"""
    if admin_user.email != SUPER_ADMIN_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can revoke subscriptions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Store old values for logging
    old_tier = user.subscription_tier
    old_end_date = user.subscription_end_date
    
    # Revoke subscription
    user.subscription_tier = SubscriptionTier.FREE
    user.subscription_end_date = None
    user.stripe_subscription_id = None
    
    # Log action
    log_admin_action(
        db=db,
        admin=admin_user,
        action_type="revoke_subscription",
        target_user_id=user.id,
        details={
            "old_tier": old_tier.value if old_tier else None,
            "old_end_date": old_end_date.isoformat() if old_end_date else None,
            "reason": reason,
            "revoked_by": admin_user.email
        },
        request=req
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Subscription revoked for user {user.email}"
    }