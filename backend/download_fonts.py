"""
Modernes Font Download Script für 2025
Lädt alle benötigten Fonts von Google Fonts und CDNs herunter
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.font_manager import FontManager

def main():
    print("🎨 Watermark-AI Font Setup")
    print("=" * 60)
    print("Dieses Script lädt alle benötigten Schriftarten herunter.")
    print("Quelle: Google Fonts & jsDelivr CDN")
    print("=" * 60)
    
    # Initialize Font Manager
    font_manager = FontManager()
    
    # Download all fonts
    font_manager.download_all_fonts()
    
    print("\n✅ Font setup complete!")
    print("\nDu kannst jetzt den Server starten:")
    print("  uvicorn main:app --reload")

if __name__ == "__main__":
    main()