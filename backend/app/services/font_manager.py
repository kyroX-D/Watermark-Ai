# File: backend/app/services/font_manager.py

import os
import requests
from pathlib import Path
from typing import Dict, Optional
import json
from datetime import datetime, timedelta

class FontManager:
    """Modern font management system using Google Fonts API"""
    
    # Extended font collection with Google Fonts
    FONT_URLS = {
        "Arial": {
            "name": "Open Sans",
            "url": "https://github.com/googlefonts/opensans/raw/main/fonts/ttf/OpenSans-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/opensans/v40/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4gaVc.ttf"
        },
        "Open Sans": {
            "name": "Open Sans",
            "url": "https://github.com/googlefonts/opensans/raw/main/fonts/ttf/OpenSans-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/opensans/v40/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4gaVc.ttf"
        },
        "Times New Roman": {
            "name": "Merriweather",
            "url": "https://github.com/SorkinType/Merriweather/raw/master/fonts/ttf/Merriweather-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/merriweather/v30/u-440qyriQwlOrhSvowK_l5OeyxNV-bnrw.ttf"
        },
        "Courier New": {
            "name": "Roboto Mono",
            "url": "https://github.com/googlefonts/RobotoMono/raw/main/fonts/ttf/RobotoMono-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/robotomono/v23/L0xTDF4xlVMF-BfR8bXMIhJHg45mwgGEFl0_3vrtSM1J-gEPT5Ese6hmHSh0mf0h.ttf"
        },
        "Georgia": {
            "name": "Playfair Display",
            "url": "https://github.com/clauseggers/Playfair/raw/master/fonts/ttf/PlayfairDisplay-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/playfairdisplay/v37/nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKdFvXDXbtM.ttf"
        },
        "Playfair Display": {
            "name": "Playfair Display",
            "url": "https://github.com/clauseggers/Playfair/raw/master/fonts/ttf/PlayfairDisplay-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/playfairdisplay/v37/nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKdFvXDXbtM.ttf"
        },
        "Verdana": {
            "name": "Nunito",
            "url": "https://raw.githubusercontent.com/googlefonts/nunito/main/fonts/variable/Nunito[wght].ttf",
            "fallback": "https://fonts.gstatic.com/s/nunito/v26/XRXI3I6Li01BKofiOc5wtlZ2di8HDLshdTk3j77e.ttf"
        },
        "Inter": {
            "name": "Inter",
            "url": "https://github.com/rsms/inter/releases/download/v4.0/Inter-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hjg.ttf"
        },
        "Montserrat": {
            "name": "Montserrat",
            "url": "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/montserrat/v26/JTUSjIg1_i6t8kCHKm459WlhyyTh89Y.ttf"
        },
        "Poppins": {
            "name": "Poppins",
            "url": "https://raw.githubusercontent.com/itfoundry/poppins/master/products/Poppins-4.003-GoogleFonts-TTF/Poppins-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/poppins/v21/pxiEyp8kv8JHgFVrJJfecnFHGPc.ttf"
        },
        "Roboto": {
            "name": "Roboto",
            "url": "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxKKTU1Kg.ttf"
        },
        "Lato": {
            "name": "Lato",
            "url": "https://raw.githubusercontent.com/googlefonts/LatoGFVersion/main/fonts/Lato-Regular.ttf",
            "fallback": "https://fonts.gstatic.com/s/lato/v24/S6uyw4BMUTPHjx4wXiWtFCc.ttf"
        }
    }
    
    def __init__(self, fonts_dir: str = "fonts"):
        self.fonts_dir = Path(fonts_dir)
        self.fonts_dir.mkdir(exist_ok=True)
        self.cache_file = self.fonts_dir / "font_cache.json"
        self._load_cache()
        
        # Download essential fonts on init
        self._ensure_essential_fonts()
    
    def _ensure_essential_fonts(self):
        """Ensure at least Arial/Open Sans is available"""
        essential_fonts = ["Arial", "Open Sans"]
        for font in essential_fonts:
            font_path = self.get_font_path(font)
            if not font_path or not font_path.exists():
                self.download_font(font)
    
    def _load_cache(self):
        """Load font cache metadata"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        else:
            self.cache = {}
    
    def _save_cache(self):
        """Save font cache metadata"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def download_font(self, font_key: str) -> Optional[Path]:
        """Download a font if not already cached"""
        if font_key not in self.FONT_URLS:
            print(f"Font '{font_key}' not found in registry")
            return None
        
        font_info = self.FONT_URLS[font_key]
        font_filename = f"{font_key.replace(' ', '')}.ttf"
        font_path = self.fonts_dir / font_filename
        
        # Check if font already exists and is recent
        if font_path.exists() and self._is_font_cached(font_key):
            return font_path
        
        print(f"Downloading font '{font_key}'...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/octet-stream,*/*',
        }
        
        # Try primary URL first, then fallback
        for url_type in ['url', 'fallback']:
            url = font_info[url_type]
            try:
                response = requests.get(url, timeout=30, headers=headers, allow_redirects=True)
                
                if response.status_code == 200 and len(response.content) > 1000:
                    # Save font file
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Update cache
                    self.cache[font_key] = {
                        'downloaded_at': datetime.now().isoformat(),
                        'size': len(response.content),
                        'source': url_type
                    }
                    self._save_cache()
                    
                    print(f"✅ Successfully downloaded '{font_key}' from {url_type}")
                    return font_path
                    
            except Exception as e:
                print(f"Failed to download from {url_type}: {e}")
                continue
        
        print(f"❌ Failed to download font '{font_key}'")
        return None
    
    def _is_font_cached(self, font_key: str) -> bool:
        """Check if font is cached and recent (within 30 days)"""
        if font_key not in self.cache:
            return False
        
        cached_date = datetime.fromisoformat(self.cache[font_key]['downloaded_at'])
        return (datetime.now() - cached_date) < timedelta(days=30)
    
    def download_all_fonts(self):
        """Download all registered fonts"""
        print("🚀 Downloading all fonts...")
        success_count = 0
        
        for font_key in self.FONT_URLS:
            if self.download_font(font_key):
                success_count += 1
        
        print(f"\n✅ Downloaded {success_count}/{len(self.FONT_URLS)} fonts")
    
    def get_font_path(self, font_key: str) -> Optional[Path]:
        """Get path to a font, downloading if necessary"""
        if not font_key or font_key not in self.FONT_URLS:
            return None
            
        font_filename = f"{font_key.replace(' ', '')}.ttf"
        font_path = self.fonts_dir / font_filename
        
        if font_path.exists():
            return font_path
        
        # Try to download
        return self.download_font(font_key)
    
    def list_available_fonts(self) -> Dict[str, Dict]:
        """List all available fonts with their status"""
        fonts_status = {}
        
        for font_key, font_info in self.FONT_URLS.items():
            font_filename = f"{font_key.replace(' ', '')}.ttf"
            font_path = self.fonts_dir / font_filename
            
            fonts_status[font_key] = {
                'google_name': font_info['name'],
                'installed': font_path.exists(),
                'cached_info': self.cache.get(font_key, {})
            }
        
        return fonts_status


# Standalone script zum Fonts herunterladen
if __name__ == "__main__":
    font_manager = FontManager()
    font_manager.download_all_fonts()