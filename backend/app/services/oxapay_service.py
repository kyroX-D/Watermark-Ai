import httpx
import hashlib
import hmac
from typing import Dict, Optional
from datetime import datetime

from ..core.config import settings


class OxaPayService:
    BASE_URL = "https://api.oxapay.com/v1"

    def __init__(self):
        self.merchant_id = settings.OXAPAY_MERCHANT_ID
        self.api_key = settings.OXAPAY_API_KEY

    async def create_payment(
        self, amount: float, currency: str, order_id: str, callback_url: str, email: str
    ) -> Dict:
        """Create OxaPay payment"""

        payload = {
            "merchant": self.merchant_id,
            "amount": amount,
            "currency": currency,
            "order_id": order_id,
            "callback_url": callback_url,
            "email": email,
            "return_url": f"{settings.FRONTEND_URL}/payment/success",
            "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel",
        }

        headers = {"API-KEY": self.api_key, "Content-Type": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/payment/create", json=payload, headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "payment_id": data["payment_id"],
                    "payment_url": data["payment_url"],
                    "status": "pending",
                }
            else:
                raise Exception(f"OxaPay error: {response.text}")

    async def verify_webhook(self, payload: Dict, signature: str) -> bool:
        """Verify OxaPay webhook signature"""
        message = f"{payload['payment_id']}{payload['status']}{payload['amount']}"
        expected_signature = hmac.new(
            settings.OXAPAY_WEBHOOK_SECRET.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def handle_webhook(self, payload: Dict) -> Dict:
        """Process OxaPay webhook"""
        status = payload.get("status")

        if status == "completed":
            return {
                "type": "payment_completed",
                "payment_id": payload["payment_id"],
                "order_id": payload["order_id"],
                "amount": payload["amount"],
                "currency": payload["currency"],
            }
        elif status == "failed":
            return {
                "type": "payment_failed",
                "payment_id": payload["payment_id"],
                "order_id": payload["order_id"],
            }

        return {"type": "unknown", "handled": False}
