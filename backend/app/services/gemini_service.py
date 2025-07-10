# File: backend/app/services/gemini_service.py

import google.generativeai as genai
from PIL import Image
import io
import base64
from typing import Dict, List, Tuple
import json

from ..core.config import settings


class GeminiService:
    def __init__(self):
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "dummy-api-key":
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            self.model = None
            print("Warning: Gemini API key not configured. Using default analysis.")

    async def analyze_image_for_watermark(
        self, image_bytes: bytes, watermark_text: str
    ) -> Dict:
        """Enhanced image analysis for optimal watermark placement"""
        
        # If no API key configured, return default analysis
        if not self.model:
            return self._get_default_analysis()

        # Convert bytes to PIL Image
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            print(f"Error opening image: {e}")
            return self._get_default_analysis()

        prompt = f"""
        Analyze this image for watermark placement with the text "{watermark_text}".
        Consider the following aspects:
        
        1. Identify optimal placement locations that are:
           - Visible to humans but difficult for AI to detect and remove
           - Integrated naturally into the image content
           - Not covering important subjects or focal points
        
        2. Suggest integration methods:
           - 'graffiti': If there are walls, surfaces suitable for graffiti-style text
           - 'sign': If there are existing signs, boards, or flat surfaces
           - 'texture': If the watermark can blend with textures (water, sky, grass)
           - 'overlay': Standard transparent overlay
        
        3. Analyze image characteristics:
           - Dominant colors and their hex values
           - Brightness levels in different areas
           - Texture complexity
           - Main subjects and their locations
        
        4. For robustness against AI removal:
           - Identify areas with high texture variance
           - Suggest positions that overlap multiple visual elements
           - Recommend optimal opacity based on background
        
        Provide your response in JSON format:
        {{
            "placement_suggestions": [
                {{
                    "location": "description of where to place",
                    "x": percentage from left (0-100),
                    "y": percentage from top (0-100),
                    "integration_method": "graffiti/sign/texture/overlay",
                    "color": "suggested hex color for best visibility",
                    "opacity": suggested opacity (0-1),
                    "size": "small/medium/large",
                    "rotation": angle in degrees (-45 to 45),
                    "reasoning": "why this placement is optimal"
                }}
            ],
            "scene_analysis": {{
                "description": "brief description of the image",
                "main_subjects": ["list of main subjects"],
                "avoid_areas": [
                    {{"x1": 0, "y1": 0, "x2": 100, "y2": 100, "reason": "face/important object"}}
                ]
            }},
            "dominant_colors": ["#hex1", "#hex2", "#hex3"],
            "brightness_map": {{
                "overall": "dark/medium/bright",
                "top_left": "dark/medium/bright",
                "top_right": "dark/medium/bright",
                "bottom_left": "dark/medium/bright",
                "bottom_right": "dark/medium/bright",
                "center": "dark/medium/bright"
            }},
            "texture_analysis": {{
                "complexity": "low/medium/high",
                "best_blend_areas": [
                    {{"x": 50, "y": 50, "description": "textured area description"}}
                ]
            }},
            "ai_resistance_score": 8.5,
            "suggested_style": "artistic style for watermark",
            "protection_recommendations": [
                "specific recommendations for maximum protection"
            ]
        }}
        """

        try:
            response = self.model.generate_content([prompt, image])

            # Parse JSON from response
            response_text = response.text
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]

            analysis = json.loads(response_text.strip())
            
            # Ensure all required fields exist
            self._ensure_analysis_completeness(analysis)
            
            return analysis

        except json.JSONDecodeError as e:
            print(f"Gemini JSON parse error: {e}")
            return self._get_default_analysis()
        except AttributeError as e:
            print(f"Gemini response error: {e}")
            return self._get_default_analysis()
        except Exception as e:
            print(f"Gemini API error: {type(e).__name__}: {e}")
            return self._get_default_analysis()

    def _ensure_analysis_completeness(self, analysis: Dict) -> None:
        """Ensure all required fields exist in analysis"""
        # Default placement if missing
        if "placement_suggestions" not in analysis or not analysis["placement_suggestions"]:
            analysis["placement_suggestions"] = [{
                "location": "bottom-right corner",
                "x": 80,
                "y": 90,
                "integration_method": "overlay",
                "color": "#FFFFFF",
                "opacity": 0.7,
                "size": "medium",
                "rotation": 0,
                "reasoning": "Standard placement for visibility"
            }]
        
        # Validate placement suggestions
        for suggestion in analysis["placement_suggestions"]:
            # Ensure all required fields
            suggestion.setdefault("location", "bottom-right corner")
            suggestion.setdefault("x", 80)
            suggestion.setdefault("y", 90)
            suggestion.setdefault("integration_method", "overlay")
            suggestion.setdefault("color", "#FFFFFF")
            suggestion.setdefault("opacity", 0.7)
            suggestion.setdefault("size", "medium")
            suggestion.setdefault("rotation", 0)
            suggestion.setdefault("reasoning", "Default placement")
            
            # Validate values
            suggestion["x"] = max(0, min(100, int(suggestion.get("x", 80))))
            suggestion["y"] = max(0, min(100, int(suggestion.get("y", 90))))
            suggestion["opacity"] = max(0.1, min(1.0, float(suggestion.get("opacity", 0.7))))
            suggestion["rotation"] = max(-45, min(45, int(suggestion.get("rotation", 0))))
        
        # Ensure scene analysis
        if "scene_analysis" not in analysis:
            analysis["scene_analysis"] = {
                "description": "Image analysis unavailable",
                "main_subjects": [],
                "avoid_areas": []
            }
        else:
            analysis["scene_analysis"].setdefault("description", "Image")
            analysis["scene_analysis"].setdefault("main_subjects", [])
            analysis["scene_analysis"].setdefault("avoid_areas", [])
        
        # Ensure colors
        if "dominant_colors" not in analysis or not analysis["dominant_colors"]:
            analysis["dominant_colors"] = ["#FFFFFF", "#000000", "#808080"]
        
        # Ensure brightness map
        if "brightness_map" not in analysis:
            analysis["brightness_map"] = {
                "overall": "medium",
                "top_left": "medium",
                "top_right": "medium",
                "bottom_left": "medium",
                "bottom_right": "medium",
                "center": "medium"
            }
        else:
            # Validate brightness values
            valid_brightness = ["dark", "medium", "bright"]
            for key in analysis["brightness_map"]:
                if analysis["brightness_map"][key] not in valid_brightness:
                    analysis["brightness_map"][key] = "medium"
        
        # Ensure texture analysis
        if "texture_analysis" not in analysis:
            analysis["texture_analysis"] = {
                "complexity": "medium",
                "best_blend_areas": []
            }
        else:
            analysis["texture_analysis"].setdefault("complexity", "medium")
            analysis["texture_analysis"].setdefault("best_blend_areas", [])
        
        # Ensure protection info
        if "ai_resistance_score" not in analysis:
            analysis["ai_resistance_score"] = 7.0
        else:
            # Validate score
            analysis["ai_resistance_score"] = max(1.0, min(10.0, float(analysis.get("ai_resistance_score", 7.0))))
        
        if "suggested_style" not in analysis:
            analysis["suggested_style"] = "standard"
        
        if "protection_recommendations" not in analysis:
            analysis["protection_recommendations"] = [
                "Use semi-transparent overlay for better integration",
                "Consider multiple smaller watermarks for redundancy"
            ]

    def _get_default_analysis(self) -> Dict:
        """Return comprehensive default analysis when API fails"""
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
                    "reasoning": "Standard placement with good visibility"
                },
                {
                    "location": "top-left corner",
                    "x": 20,
                    "y": 10,
                    "integration_method": "overlay",
                    "color": "#FFFFFF",
                    "opacity": 0.6,
                    "size": "small",
                    "rotation": 0,
                    "reasoning": "Alternative placement for redundancy"
                }
            ],
            "scene_analysis": {
                "description": "Image analysis unavailable",
                "main_subjects": [],
                "avoid_areas": []
            },
            "dominant_colors": ["#FFFFFF", "#000000", "#808080"],
            "brightness_map": {
                "overall": "medium",
                "top_left": "medium",
                "top_right": "medium",
                "bottom_left": "medium",
                "bottom_right": "medium",
                "center": "medium"
            },
            "texture_analysis": {
                "complexity": "medium",
                "best_blend_areas": [
                    {"x": 50, "y": 50, "description": "Center area"}
                ]
            },
            "ai_resistance_score": 7.0,
            "suggested_style": "standard",
            "protection_recommendations": [
                "Use multiple watermark layers",
                "Apply with varying opacity",
                "Consider contextual integration"
            ]
        }