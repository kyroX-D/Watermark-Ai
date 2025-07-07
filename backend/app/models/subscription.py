from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, Numeric
from datetime import datetime
import enum

from ..core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    STRIPE = "stripe"
    OXAPAY = "oxapay"
