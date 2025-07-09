# File: backend/app/utils/validators.py

from fastapi import HTTPException, UploadFile
import re
import html
from typing import Optional

# Erlaubte Bildformate
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg", 
    "image/jpg",
    "image/gif",
    "image/webp"
}

def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file"""
    
    # Check file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File size too large. Maximum size is 10MB"
        )
    
    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file extension
    filename = file.filename.lower()
    if not any(filename.endswith(f".{ext}") for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=415,
            detail=f"Invalid file extension. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def sanitize_watermark_text(text: str) -> str:
    """Sanitize watermark text to prevent XSS and injection attacks"""
    
    if not text:
        return ""
    
    # HTML escape
    text = html.escape(text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    
    # Remove potential script tags or javascript
    dangerous_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe.*?>',
        r'<object.*?>',
        r'<embed.*?>'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Limit length
    text = text[:100]
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def validate_hex_color(color: str) -> bool:
    """Validate hex color format"""
    pattern = r'^#[0-9A-Fa-f]{6}$'
    return bool(re.match(pattern, color))


def validate_position(position: str) -> bool:
    """Validate watermark position"""
    valid_positions = {
        "top-left", 
        "top-right", 
        "bottom-left", 
        "bottom-right", 
        "center",
        "ai-suggested"
    }
    return position in valid_positions


def validate_size(size: str) -> bool:
    """Validate watermark size"""
    valid_sizes = {"small", "medium", "large"}
    return size in valid_sizes


def validate_opacity(opacity: float) -> bool:
    """Validate opacity value"""
    return 0.1 <= opacity <= 1.0


def validate_font_family(font: Optional[str], user_tier: str) -> bool:
    """Validate font family based on user tier"""
    if not font:
        return True
    
    # Elite fonts only for elite users
    elite_fonts = {
        "Arial",
        "Times New Roman", 
        "Courier New",
        "Georgia",
        "Verdana"
    }
    
    if user_tier != "elite" and font in elite_fonts:
        return False
    
    return font in elite_fonts