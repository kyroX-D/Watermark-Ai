# File: backend/app/api/endpoints/webhooks.py

from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hmac
import hashlib

from ...core.database import get_db
from ...core.config import settings
from ...models.user import User, SubscriptionTier
from ...models.payment import Payment, PaymentStatus
from ...services.stripe_service import StripeService
from ...services.oxapay_service import OxaPayService

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db),
):
    """Handle Stripe webhooks"""
    payload = await request.body()

    try:
        stripe_service = StripeService()
        event = await stripe_service.handle_webhook(
            payload.decode("utf-8"), stripe_signature
        )

        if event["type"] == "subscription_created":
            # Find user and update subscription
            user = (
                db.query(User)
                .filter(User.stripe_customer_id == event["customer_id"])
                .first()
            )

            if user:
                # Determine tier from subscription
                payment = (
                    db.query(Payment)
                    .filter(Payment.provider_session_id == event.get("session_id"))
                    .first()
                )

                if payment:
                    user.subscription_tier = SubscriptionTier(payment.subscription_tier)
                    user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
                    user.stripe_subscription_id = event["subscription_id"]

                    payment.payment_status = PaymentStatus.COMPLETED
                    payment.completed_at = datetime.utcnow()

                    db.commit()

        elif event["type"] == "subscription_cancelled":
            # Find user and downgrade to free
            user = (
                db.query(User)
                .filter(User.stripe_customer_id == event["customer_id"])
                .first()
            )

            if user:
                user.subscription_tier = SubscriptionTier.FREE
                user.stripe_subscription_id = None
                db.commit()

        return {"received": True}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/oxapay")
async def oxapay_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle OxaPay webhooks"""
    payload = await request.json()
    signature = request.headers.get("X-OxaPay-Signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        oxapay_service = OxaPayService()

        # Verify webhook signature
        if not await oxapay_service.verify_webhook(payload, signature):
            raise HTTPException(status_code=400, detail="Invalid signature")

        event = await oxapay_service.handle_webhook(payload)

        if event["type"] == "payment_completed":
            # Find payment record
            payment = (
                db.query(Payment).filter(Payment.id == int(event["order_id"])).first()
            )

            if payment:
                payment.payment_status = PaymentStatus.COMPLETED
                payment.completed_at = datetime.utcnow()
                payment.provider_payment_id = event["payment_id"]

                # Update user subscription
                user = db.query(User).filter(User.id == payment.user_id).first()
                if user:
                    user.subscription_tier = SubscriptionTier(payment.subscription_tier)
                    user.subscription_end_date = datetime.utcnow() + timedelta(days=30)

                db.commit()

        elif event["type"] == "payment_failed":
            payment = (
                db.query(Payment)
                .filter(Payment.provider_payment_id == event["payment_id"])
                .first()
            )

            if payment:
                payment.payment_status = PaymentStatus.FAILED
                db.commit()

        return {"received": True}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))