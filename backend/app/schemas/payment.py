from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.payment import PaymentStatus, PaymentMethod


class PaymentBase(BaseModel):
    amount: float
    currency: str
    payment_method: PaymentMethod
    subscription_tier: str


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    payment_status: PaymentStatus
    provider_payment_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        orm_mode = True
        from_attributes = True
