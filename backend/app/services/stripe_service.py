import stripe
from datetime import datetime, timedelta
from typing import Dict, Optional

from ..core.config import settings
from ..models.user import SubscriptionTier

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:

    @staticmethod
    async def create_customer(email: str, name: str) -> str:
        """Create a Stripe customer"""
        customer = stripe.Customer.create(email=email, name=name)
        return customer.id

    @staticmethod
    async def create_checkout_session(
        customer_id: str, price_id: str, success_url: str, cancel_url: str
    ) -> Dict:
        """Create Stripe checkout session"""
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"customer_id": customer_id},
        )
        return {"session_id": session.id, "url": session.url}

    @staticmethod
    async def cancel_subscription(subscription_id: str) -> bool:
        """Cancel a subscription"""
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception as e:
            print(f"Error canceling subscription: {e}")
            return False

    @staticmethod
    async def handle_webhook(payload: Dict, sig_header: str) -> Dict:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )

            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                return {
                    "type": "subscription_created",
                    "customer_id": session["customer"],
                    "subscription_id": session["subscription"],
                    "status": "active",
                }

            elif event["type"] == "customer.subscription.deleted":
                subscription = event["data"]["object"]
                return {
                    "type": "subscription_cancelled",
                    "customer_id": subscription["customer"],
                    "subscription_id": subscription["id"],
                    "status": "cancelled",
                }

            return {"type": event["type"], "handled": False}

        except Exception as e:
            raise ValueError(f"Webhook error: {str(e)}")
