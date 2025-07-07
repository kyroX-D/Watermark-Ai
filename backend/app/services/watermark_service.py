from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import os
import uuid
from typing import Tuple, Dict, Optional
import numpy as np
import time

from .gemini_service import GeminiService
from ..core.config import settings


class WatermarkService:
    def __init__(self):
        self.gemini_service = GeminiService()

    async def apply_intelligent_watermark(
        self, image_bytes: bytes, watermark_text: str, user_tier: str
    ) -> Tuple[bytes, Dict]:
        """Apply AI-guided watermark to image"""

        start_time = time.time()

        # Get AI analysis
        analysis = await self.gemini_service.analyze_image_for_watermark(
            image_bytes, watermark_text
        )

        # Open image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        # Apply resolution limits based on tier
        image = self._apply_resolution_limit(image, user_tier)

        # Get best placement suggestion
        placement = analysis["placement_suggestions"][0]

        # Apply watermark based on integration method
        if placement["integration_method"] == "graffiti":
            watermarked = self._apply_graffiti_watermark(
                image, watermark_text, placement
            )
        elif placement["integration_method"] == "texture":
            watermarked = self._apply_texture_watermark(
                image, watermark_text, placement
            )
        else:
            watermarked = self._apply_standard_watermark(
                image, watermark_text, placement
            )

        # Convert to bytes
        output = io.BytesIO()
        watermarked.save(output, format="PNG", quality=95)
        output.seek(0)

        # Add processing time to analysis
        analysis["processing_time"] = int((time.time() - start_time) * 1000)

        return output.getvalue(), analysis
