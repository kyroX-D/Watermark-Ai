from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base


class Watermark(Base):
    __tablename__ = "watermarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Image data
    original_image_url = Column(String, nullable=False)
    watermarked_image_url = Column(String, nullable=False)
    watermark_text = Column(String, nullable=False)

    # AI analysis data
    ai_analysis = Column(JSON, nullable=True)  # Stores Gemini Vision analysis
    placement_data = Column(JSON, nullable=True)  # Stores watermark placement info

    # Metadata
    image_width = Column(Integer)
    image_height = Column(Integer)
    file_size = Column(Integer)  # in bytes
    processing_time = Column(Integer)  # in milliseconds

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="watermarks")
