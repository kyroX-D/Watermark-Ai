from pydantic import BaseModel, HttpUrl, validator
from typing import Optional
from datetime import datetime


class SubscriptionCreate(BaseModel):
    price_id: str
    success_url: HttpUrl
    cancel_url: HttpUrl


class CryptoPaymentCreate(BaseModel):
    plan_id: str
    amount: int
    currency: str = "USDT"

    @validator("currency")
    def validate_currency(cls, v):
        allowed = ["USDT", "ETH", "BTC"]
        if v not in allowed:
            raise ValueError(f"Currency must be one of {allowed}")
        return v

    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class PaymentSessionResponse(BaseModel):
    session_id: str
    url: str


class SubscriptionResponse(BaseModel):
    tier: str
    is_active: bool
    end_date: Optional[datetime]
    stripe_subscription_id: Optional[str]
