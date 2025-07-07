import google.generativeai as genai
from PIL import Image
import io
import base64
from typing import Dict, List, Tuple
import json

from ..core.config import settings


class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def analyze_image_for_watermark(
        self, image_bytes: bytes, watermark_text: str
    ) -> Dict:
        """Analyze image and determine optimal watermark placement"""

        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        prompt = f"""
        Analyze this image and determine the best location to embed a watermark with the text "{watermark_text}".
        The watermark should be integrated naturally into the image content (e.g., as graffiti on a wall, 
        text on a sign, or blended into textures like grass or water).
        
        Provide your response in JSON format with:
        {{
            "placement_suggestions": [
                {{
                    "location": "description of where to place",
                    "x": percentage from left (0-100),
                    "y": percentage from top (0-100),
                    "integration_method": "how to blend (e.g., 'graffiti', 'sign', 'texture')",
                    "color": "suggested hex color",
                    "opacity": suggested opacity (0-1),
                    "size": "small/medium/large",
                    "rotation": angle in degrees
                }}
            ],
            "scene_description": "brief description of the image",
            "dominant_colors": ["hex colors"],
            "suggested_style": "artistic style for watermark"
        }}
        """

        try:
            response = self.model.generate_content([prompt, image])

            # Parse JSON from response
            response_text = response.text
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]

            analysis = json.loads(response_text.strip())
            return analysis

        except Exception as e:
            print(f"Gemini analysis error: {e}")
            # Return default placement if analysis fails
            return {
                "placement_suggestions": [
                    {
                        "location": "bottom-right corner",
                        "x": 80,
                        "y": 90,
                        "integration_method": "overlay",
                        "color": "#FFFFFF",
                        "opacity": 0.7,
                        "size": "medium",
                        "rotation": 0,
                    }
                ],
                "scene_description": "Image analysis unavailable",
                "dominant_colors": ["#FFFFFF", "#000000"],
                "suggested_style": "standard",
            }
