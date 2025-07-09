# File: backend/app/services/watermark_service.py

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor, ImageEnhance
import io
import os
import uuid
from typing import Tuple, Dict, Optional, List
import numpy as np
import time
from pathlib import Path
import math

from .gemini_service import GeminiService
from .font_manager import FontManager
from ..core.config import settings


class WatermarkService:
    def __init__(self):
        self.gemini_service = GeminiService()
        
        # Initialize Font Manager
        self.font_manager = FontManager()
        
        # Download default font if not present
        self.font_manager.download_font("Arial")
        
        # Elite fonts mapping (erweitert mit Google Fonts)
        self.elite_fonts = {
            'Arial': 'Arial',
            'Times New Roman': 'Times New Roman',
            'Courier New': 'Courier New',
            'Georgia': 'Georgia',
            'Verdana': 'Verdana',
            'Inter': 'Inter',
            'Montserrat': 'Montserrat',
            'Poppins': 'Poppins',
            'Roboto': 'Roboto',
            'Lato': 'Lato',
            'Open Sans': 'Open Sans',
            'Playfair Display': 'Playfair Display'
        }

    async def apply_intelligent_watermark(
        self, 
        image_bytes: bytes, 
        watermark_text: str, 
        user_tier: str,
        # Erweiterte Parameter
        text_position: str = "bottom-right",
        text_size: str = "medium",
        text_opacity: float = 0.7,
        auto_opacity: bool = False,
        multiple_watermarks: bool = False,
        watermark_pattern: str = "diagonal",  # diagonal, grid, random
        font_family: Optional[str] = None,
        text_color: str = "#FFFFFF",
        text_shadow: bool = False,
        protection_mode: str = "standard"  # standard, contextual, multilayer
    ) -> Tuple[bytes, Dict]:
        """Apply AI-guided watermark with enhanced protection strategies"""

        start_time = time.time()

        # Get AI analysis
        analysis = await self.gemini_service.analyze_image_for_watermark(
            image_bytes, watermark_text
        )

        # Open image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        # Apply resolution limits based on tier
        image = self._apply_resolution_limit(image, user_tier)

        # Auto-Opacity wenn aktiviert
        if auto_opacity:
            text_opacity = await self._calculate_auto_opacity(image, analysis)
            analysis["auto_opacity_value"] = text_opacity

        # Position bestimmen
        if text_position == "auto":
            # AI wählt beste Position
            placement = analysis["placement_suggestions"][0]
            analysis["auto_position_selected"] = placement["location"]
        else:
            placement = {
                "location": text_position,
                "x": self._get_position_coordinates(text_position)[0],
                "y": self._get_position_coordinates(text_position)[1],
                "integration_method": "overlay",
                "color": text_color,
                "opacity": text_opacity,
                "size": text_size,
                "rotation": 0
            }

        # Font selection
        font_path = self._get_font_path(font_family, user_tier)

        # Apply watermark based on protection mode
        if protection_mode == "multilayer":
            watermarked = await self._apply_multilayer_watermark(
                image, watermark_text, placement, font_path, text_shadow, analysis
            )
        elif protection_mode == "contextual" and text_position == "auto":
            watermarked = await self._apply_contextual_watermark(
                image, watermark_text, placement, font_path, analysis
            )
        elif multiple_watermarks:
            watermarked = self._apply_multiple_watermarks(
                image, watermark_text, placement, font_path, watermark_pattern, text_shadow
            )
        else:
            watermarked = self._apply_standard_watermark(
                image, watermark_text, placement, font_path, text_shadow
            )

        # Convert to bytes
        output = io.BytesIO()
        watermarked.save(output, format="PNG", quality=95)
        output.seek(0)

        # Add processing info to analysis
        analysis["processing_time"] = int((time.time() - start_time) * 1000)
        analysis["custom_settings"] = {
            "position": text_position,
            "size": text_size,
            "opacity": text_opacity,
            "auto_opacity": auto_opacity,
            "multiple_watermarks": multiple_watermarks,
            "pattern": watermark_pattern if multiple_watermarks else None,
            "font": font_family if user_tier in ["pro", "elite"] else "default",
            "color": text_color,
            "shadow": text_shadow and user_tier == "elite",
            "protection_mode": protection_mode
        }

        return output.getvalue(), analysis

    async def _calculate_auto_opacity(self, image: Image.Image, analysis: Dict) -> float:
        """AI-based automatic opacity calculation for optimal visibility and protection"""
        # Analysiere Bildhelligkeit und Kontrast
        grayscale = image.convert('L')
        pixels = np.array(grayscale)
        
        # Berechne durchschnittliche Helligkeit
        avg_brightness = np.mean(pixels) / 255.0
        
        # Berechne Standardabweichung für Kontrast
        std_brightness = np.std(pixels) / 255.0
        
        # Berücksichtige AI-Analyse
        scene_complexity = len(analysis.get("dominant_colors", [])) / 10.0
        
        # Formel für optimale Opacity
        # Dunkle Bilder = höhere Opacity, Helle Bilder = niedrigere Opacity
        # Hoher Kontrast = niedrigere Opacity, Niedriger Kontrast = höhere Opacity
        base_opacity = 0.7
        brightness_factor = (1 - avg_brightness) * 0.3
        contrast_factor = (1 - std_brightness) * 0.2
        complexity_factor = scene_complexity * 0.1
        
        optimal_opacity = base_opacity + brightness_factor - contrast_factor + complexity_factor
        
        # Clamp zwischen 0.4 und 0.9 für beste Sichtbarkeit und Schutz
        return max(0.4, min(0.9, optimal_opacity))

    def _apply_multiple_watermarks(
        self, 
        image: Image.Image, 
        text: str, 
        base_placement: Dict,
        font_path: Path,
        pattern: str,
        text_shadow: bool
    ) -> Image.Image:
        """Apply multiple watermarks in various patterns"""
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Font setup
        font_size = self._calculate_font_size(
            image.width, 
            image.height, 
            base_placement.get("size", "medium")
        )
        
        try:
            font = ImageFont.truetype(str(font_path), font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Color with opacity
        color = self._hex_to_rgba(base_placement.get("color", "#FFFFFF"), base_placement.get("opacity", 0.7))
        
        positions = []
        
        if pattern == "diagonal":
            # Diagonal pattern from bottom-left to top-right
            num_watermarks = 5
            for i in range(num_watermarks):
                progress = i / (num_watermarks - 1)
                x = int(progress * (image.width - text_width))
                y = int((1 - progress) * (image.height - text_height))
                positions.append((x, y))
                
        elif pattern == "grid":
            # Grid pattern
            cols = 3
            rows = 3
            x_spacing = image.width / (cols + 1)
            y_spacing = image.height / (rows + 1)
            
            for row in range(1, rows + 1):
                for col in range(1, cols + 1):
                    x = int(col * x_spacing - text_width / 2)
                    y = int(row * y_spacing - text_height / 2)
                    positions.append((x, y))
                    
        elif pattern == "random":
            # Random pattern with collision avoidance
            num_watermarks = 7
            min_distance = max(text_width, text_height) * 1.5
            
            for _ in range(num_watermarks):
                attempts = 0
                while attempts < 50:
                    x = np.random.randint(0, max(1, image.width - text_width))
                    y = np.random.randint(0, max(1, image.height - text_height))
                    
                    # Check collision with existing positions
                    valid = True
                    for px, py in positions:
                        distance = math.sqrt((x - px)**2 + (y - py)**2)
                        if distance < min_distance:
                            valid = False
                            break
                    
                    if valid:
                        positions.append((x, y))
                        break
                    attempts += 1
        
        # Draw all watermarks
        for x, y in positions:
            if text_shadow:
                shadow_offset = 2
                shadow_color = self._hex_to_rgba("#000000", 0.5)
                draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
            
            draw.text((x, y), text, font=font, fill=color)
        
        # Composite
        watermarked = Image.alpha_composite(image, overlay)
        return watermarked

    async def _apply_multilayer_watermark(
        self,
        image: Image.Image,
        text: str,
        placement: Dict,
        font_path: Path,
        text_shadow: bool,
        analysis: Dict
    ) -> Image.Image:
        """Apply multilayer watermark for enhanced protection"""
        # Layer 1: Standard visible watermark
        watermarked = self._apply_standard_watermark(
            image, text, placement, font_path, text_shadow
        )
        
        # Layer 2: Semi-transparent displaced layer
        overlay = Image.new("RGBA", watermarked.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate displacement based on image analysis
        displacement_x = int(image.width * 0.05)
        displacement_y = int(image.height * 0.05)
        
        # Modified placement for second layer
        displaced_placement = placement.copy()
        displaced_placement["x"] = (placement["x"] + 5) % 100
        displaced_placement["y"] = (placement["y"] + 5) % 100
        displaced_placement["opacity"] = placement["opacity"] * 0.3  # More transparent
        
        # Apply slight distortion to second layer
        font_size = self._calculate_font_size(
            image.width, 
            image.height, 
            placement.get("size", "medium")
        ) * 0.9  # Slightly smaller
        
        try:
            font = ImageFont.truetype(str(font_path), int(font_size))
        except:
            font = ImageFont.load_default()
        
        # Calculate position for displaced layer
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = int((displaced_placement["x"] / 100) * image.width - text_width / 2) + displacement_x
        y = int((displaced_placement["y"] / 100) * image.height - text_height / 2) + displacement_y
        
        # Ensure within bounds
        x = max(10, min(x, image.width - text_width - 10))
        y = max(10, min(y, image.height - text_height - 10))
        
        # Different color for second layer (slightly shifted hue)
        base_color = ImageColor.getrgb(placement.get("color", "#FFFFFF"))
        shifted_color = (
            (base_color[0] + 30) % 255,
            (base_color[1] + 30) % 255,
            (base_color[2] + 30) % 255,
            int(255 * displaced_placement["opacity"])
        )
        
        # Draw displaced layer
        draw.text((x, y), text, font=font, fill=shifted_color)
        
        # Apply slight blur to displaced layer
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=1))
        
        # Composite
        final_watermarked = Image.alpha_composite(watermarked, overlay)
        
        return final_watermarked

    async def _apply_contextual_watermark(
        self,
        image: Image.Image,
        text: str,
        placement: Dict,
        font_path: Path,
        analysis: Dict
    ) -> Image.Image:
        """Apply contextual watermark that blends with image content"""
        # Use AI suggestion for integration method
        integration_method = placement.get("integration_method", "overlay")
        
        if integration_method == "graffiti":
            # Apply with texture and distortion
            watermarked = self._apply_graffiti_watermark(
                image, text, placement, font_path, True
            )
            
            # Add weathering effect
            enhancer = ImageEnhance.Contrast(watermarked)
            watermarked = enhancer.enhance(0.95)
            
        elif integration_method == "sign":
            # Apply as if on a sign or surface
            watermarked = self._apply_surface_watermark(
                image, text, placement, font_path
            )
            
        elif integration_method == "texture":
            # Blend with existing textures
            watermarked = self._apply_texture_watermark(
                image, text, placement, font_path
            )
            
            # Apply adaptive blending based on surrounding colors
            if "dominant_colors" in analysis:
                watermarked = self._adaptive_color_blend(
                    watermarked, placement, analysis["dominant_colors"]
                )
        else:
            # Default to standard with contextual adjustments
            watermarked = self._apply_standard_watermark(
                image, text, placement, font_path, True
            )
        
        return watermarked

    def _apply_surface_watermark(
        self,
        image: Image.Image,
        text: str,
        placement: Dict,
        font_path: Path
    ) -> Image.Image:
        """Apply watermark as if on a surface with perspective"""
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate font size
        font_size = self._calculate_font_size(
            image.width, 
            image.height, 
            placement.get("size", "medium")
        )
        
        try:
            font = ImageFont.truetype(str(font_path), font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        x = int((placement["x"] / 100) * image.width - text_width / 2)
        y = int((placement["y"] / 100) * image.height - text_height / 2)
        
        # Create text on separate image for transformation
        text_img = Image.new("RGBA", (text_width + 20, text_height + 20), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        
        # Add subtle background
        background_color = self._hex_to_rgba("#000000", 0.3)
        text_draw.rectangle(
            [(5, 5), (text_width + 15, text_height + 15)],
            fill=background_color
        )
        
        # Draw text
        color = self._hex_to_rgba(placement.get("color", "#FFFFFF"), placement.get("opacity", 0.7))
        text_draw.text((10, 10), text, font=font, fill=color)
        
        # Apply slight perspective transform if needed
        if placement.get("rotation", 0) != 0:
            text_img = text_img.rotate(placement["rotation"], expand=1)
        
        # Paste onto overlay
        overlay.paste(text_img, (x, y), text_img)
        
        # Composite
        watermarked = Image.alpha_composite(image, overlay)
        return watermarked

    def _adaptive_color_blend(
        self,
        image: Image.Image,
        placement: Dict,
        dominant_colors: List[str]
    ) -> Image.Image:
        """Adaptively blend watermark color with image colors"""
        # This is a placeholder for adaptive color blending
        # In production, this would analyze surrounding pixels
        # and adjust watermark color for better integration
        return image

    def _apply_resolution_limit(self, image: Image.Image, user_tier: str) -> Image.Image:
        """Apply resolution limits based on subscription tier"""
        max_resolutions = {
            "free": settings.FREE_MAX_RESOLUTION,
            "pro": settings.PRO_MAX_RESOLUTION,
            "elite": settings.ELITE_MAX_RESOLUTION,
        }
        
        max_res = max_resolutions.get(user_tier, settings.FREE_MAX_RESOLUTION)
        
        if image.width > max_res or image.height > max_res:
            ratio = min(max_res / image.width, max_res / image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image

    def _get_font_path(self, font_family: Optional[str], user_tier: str) -> Path:
        """Get font path based on user tier and selection"""
        if not font_family or font_family not in self.elite_fonts:
            font_family = "Arial"
        
        # Elite fonts nur für Elite-User
        if user_tier != "elite" and font_family not in ["Arial", "Open Sans"]:
            font_family = "Arial"
        
        font_path = self.font_manager.get_font_path(font_family)
        
        if font_path and font_path.exists():
            return font_path
        else:
            return self.font_manager.get_font_path("Arial") or Path("fonts/Arial.ttf")

    def _get_position_coordinates(self, position: str) -> Tuple[int, int]:
        """Convert position string to percentage coordinates"""
        positions = {
            "top-left": (10, 10),
            "top-right": (90, 10),
            "bottom-left": (10, 90),
            "bottom-right": (90, 90),
            "center": (50, 50),
            "top-center": (50, 10),
            "bottom-center": (50, 90),
            "left-center": (10, 50),
            "right-center": (90, 50)
        }
        return positions.get(position, (90, 90))

    def _calculate_font_size(self, image_width: int, image_height: int, size: str) -> int:
        """Calculate font size based on image dimensions"""
        base_size = min(image_width, image_height) // 20
        
        size_multipliers = {
            "small": 0.7,
            "medium": 1.0,
            "large": 1.5
        }
        
        return int(base_size * size_multipliers.get(size, 1.0))

    def _apply_standard_watermark(
        self, 
        image: Image.Image, 
        text: str, 
        placement: Dict,
        font_path: Path,
        text_shadow: bool = False
    ) -> Image.Image:
        """Apply standard overlay watermark"""
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        font_size = self._calculate_font_size(
            image.width, 
            image.height, 
            placement.get("size", "medium")
        )
        
        try:
            font = ImageFont.truetype(str(font_path), font_size)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = int((placement["x"] / 100) * image.width - text_width / 2)
        y = int((placement["y"] / 100) * image.height - text_height / 2)
        
        x = max(10, min(x, image.width - text_width - 10))
        y = max(10, min(y, image.height - text_height - 10))
        
        color = self._hex_to_rgba(placement.get("color", "#FFFFFF"), placement.get("opacity", 0.7))
        
        if text_shadow:
            shadow_offset = 2
            shadow_color = self._hex_to_rgba("#000000", 0.5)
            draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
        
        draw.text((x, y), text, font=font, fill=color)
        
        if placement.get("rotation", 0) != 0:
            overlay = overlay.rotate(placement["rotation"], expand=1)
        
        watermarked = Image.alpha_composite(image, overlay)
        
        return watermarked

    def _apply_graffiti_watermark(
        self, 
        image: Image.Image, 
        text: str, 
        placement: Dict,
        font_path: Path,
        text_shadow: bool = False
    ) -> Image.Image:
        """Apply graffiti-style watermark with texture"""
        watermarked = self._apply_standard_watermark(image, text, placement, font_path, text_shadow)
        
        # Add texture and weathering effects here
        # This is a simplified version
        
        return watermarked

    def _apply_texture_watermark(
        self, 
        image: Image.Image, 
        text: str, 
        placement: Dict,
        font_path: Path
    ) -> Image.Image:
        """Apply texture-blended watermark"""
        watermarked = self._apply_standard_watermark(image, text, placement, font_path, False)
        
        # Add texture blending logic here
        
        return watermarked

    def _hex_to_rgba(self, hex_color: str, opacity: float) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA tuple"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (*rgb, int(255 * opacity))

    async def save_watermarked_image(self, image_bytes: bytes, filename: str) -> str:
        """Save watermarked image to storage"""
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        
        return f"watermarks/{unique_filename}"