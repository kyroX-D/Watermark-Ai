from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    Boolean,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base
from .subscription import PaymentStatus, PaymentMethod


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="EUR")
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # Provider specific
    provider_payment_id = Column(String, unique=True, nullable=True)  # Stripe/OxaPay ID
    provider_session_id = Column(String, unique=True, nullable=True)

    # Subscription details
    subscription_tier = Column(String, nullable=False)
    subscription_months = Column(Integer, default=1)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")
