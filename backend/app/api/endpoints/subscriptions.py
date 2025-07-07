from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from typing import Dict

from ...core.database import get_db
from ...core.security import get_current_active_user
from ...core.config import settings
from ...models.user import User, SubscriptionTier
from ...models.payment import Payment, PaymentStatus, PaymentMethod
from ...schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    PaymentSessionResponse,
    CryptoPaymentCreate,
)
from ...services.stripe_service import StripeService
from ...services.oxapay_service import OxaPayService

router = APIRouter()


@router.post("/create-checkout", response_model=PaymentSessionResponse)
async def create_stripe_checkout(
    data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create Stripe checkout session"""
    if not current_user.stripe_customer_id:
        # Create Stripe customer if not exists
        stripe_service = StripeService()
        current_user.stripe_customer_id = await stripe_service.create_customer(
            current_user.email, current_user.username
        )
        db.commit()

    # Get price ID based on plan
    price_map = {"pro": settings.STRIPE_PRICE_PRO, "elite": settings.STRIPE_PRICE_ELITE}

    price_id = price_map.get(data.price_id, data.price_id)

    stripe_service = StripeService()
    session = await stripe_service.create_checkout_session(
        customer_id=current_user.stripe_customer_id,
        price_id=price_id,
        success_url=data.success_url,
        cancel_url=data.cancel_url,
    )

    # Create pending payment record
    payment = Payment(
        user_id=current_user.id,
        amount=20.0 if "pro" in price_id else 50.0,
        currency="EUR",
        payment_method=PaymentMethod.STRIPE,
        payment_status=PaymentStatus.PENDING,
        provider_session_id=session["session_id"],
        subscription_tier="pro" if "pro" in price_id else "elite",
        subscription_months=1,
    )
    db.add(payment)
    db.commit()

    return PaymentSessionResponse(session_id=session["session_id"], url=session["url"])


@router.post("/create-crypto-payment", response_model=Dict)
async def create_crypto_payment(
    data: CryptoPaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create OxaPay crypto payment"""
    oxapay_service = OxaPayService()

    # Create payment record
    payment = Payment(
        user_id=current_user.id,
        amount=float(data.amount),
        currency=data.currency,
        payment_method=PaymentMethod.OXAPAY,
        payment_status=PaymentStatus.PENDING,
        subscription_tier=data.plan_id,
        subscription_months=1,
    )
    db.add(payment)
    db.commit()

    # Create OxaPay payment
    payment_data = await oxapay_service.create_payment(
        amount=float(data.amount),
        currency=data.currency,
        order_id=str(payment.id),
        callback_url=f"{settings.API_URL}/api/webhooks/oxapay",
        email=current_user.email,
    )

    # Update payment with provider ID
    payment.provider_payment_id = payment_data["payment_id"]
    db.commit()

    return {
        "payment_id": payment_data["payment_id"],
        "payment_url": payment_data["payment_url"],
    }


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Cancel subscription"""
    if not current_user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    stripe_service = StripeService()
    success = await stripe_service.cancel_subscription(
        current_user.stripe_subscription_id
    )

    if success:
        # Subscription will remain active until end date
        return {
            "message": "Subscription cancelled. Access will continue until the end of the billing period."
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to cancel subscription")


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_active_user),
):
    """Get current subscription details"""
    return SubscriptionResponse(
        tier=current_user.subscription_tier,
        is_active=current_user.subscription_tier != SubscriptionTier.FREE,
        end_date=current_user.subscription_end_date,
        stripe_subscription_id=current_user.stripe_subscription_id,
    )
