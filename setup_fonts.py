#!/usr/bin/env python3
"""
Setup script per scaricare e installare i font Material Icons
"""

import os
import urllib.request
import zipfile
import shutil
from pathlib import Path


def download_material_icons_font():
    """Scarica e installa il font Material Icons"""
    print("🎨 Setup Material Icons Font...")
    
    # URL per il font Material Icons
    font_url = "https://github.com/google/material-design-icons/blob/master/font/MaterialIcons-Regular.ttf?raw=true"
    
    # Directory fonts
    fonts_dir = Path(__file__).parent / "fonts"
    fonts_dir.mkdir(exist_ok=True)
    
    font_path = fonts_dir / "MaterialIcons-Regular.ttf"
    
    try:
        if not font_path.exists():
            print("📥 Downloading Material Icons font...")
            urllib.request.urlretrieve(font_url, font_path)
            print(f"✅ Font salvato in: {font_path}")
        else:
            print(f"✅ Font già presente: {font_path}")
            
        return True
        
    except Exception as e:
        print(f"❌ Errore download font: {e}")
        
        # Font fallback (usa emoji)
        print("📝 Creando fallback per Material Icons...")
        create_fallback_icons()
        return False


def create_fallback_icons():
    """Crea fallback emoji per Material Icons"""
    fallback_code = '''"""
Fallback Material Icons con emoji
"""

class MaterialIconsFallback:
    """Fallback icons con emoji quando Material Icons non è disponibile"""
    
    ICONS = {
        # Navigation
        'home': '🏠',
        'arrow_back': '⬅️',
        'arrow_forward': '➡️',
        'arrow_upward': '⬆️',
        'arrow_downward': '⬇️',
        'menu': '☰',
        'close': '✖️',
        'more_vert': '⋮',
        'more_horiz': '⋯',
        'expand_less': '⌄',
        'expand_more': '⌃',
        'refresh': '🔄',
        
        # Action
        'search': '🔍',
        'add': '➕',
        'remove': '➖',
        'edit': '✏️',
        'delete': '🗑️',
        'save': '💾',
        'favorite': '❤️',
        'share': '📤',
        'visibility': '👁️',
        'visibility_off': '👁️‍🗨️',
        'thumb_up': '👍',
        'thumb_down': '👎',
        'star': '⭐',
        'star_border': '☆',
        
        # Communication
        'chat': '💬',
        'message': '✉️',
        'call': '📞',
        'mail': '📧',
        'forum': '💭',
        
        # Device
        'camera': '📷',
        'camera_alt': '📸',
        'photo_camera': '📷',
        'videocam': '🎥',
        'mic': '🎤',
        'location_on': '📍',
        'gps_fixed': '🎯',
        
        # File
        'folder': '📁',
        'folder_open': '📂',
        'insert_drive_file': '📄',
        'image': '🖼️',
        'photo': '🏞️',
        'video_library': '📹',
        'music_note': '🎵',
        
        # Maps
        'map': '🗺️',
        'place': '📍',
        'navigation': '🧭',
        'directions': '🧭',
        'my_location': '📍',
        'layers': '📋',
        
        # Social
        'people': '👥',
        'person': '👤',
        'person_add': '👤➕',
        'group': '👫',
        'public': '🌍',
        
        # Notification
        'notifications': '🔔',
        'notifications_off': '🔕',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️',
        
        # Theme
        'brightness_high': '☀️',
        'brightness_low': '🌙',
        'dark_mode': '🌙',
        'light_mode': '☀️',
        
        # Custom app-specific
        'monument': '🏛️',
        'achievement': '🏆',
        'leaderboard': '📊',
        'camera_enhanced': '📷',
        'ar_view': '👁️‍🗨️',
        'analytics': '📈',
        'gamification': '🎮',
    }
    
    @classmethod
    def get_icon(cls, name: str, fallback: str = '?') -> str:
        return cls.ICONS.get(name, fallback)
    
    @classmethod
    def is_available(cls, name: str) -> bool:
        return name in cls.ICONS

# Usa il fallback se Material Icons non è disponibile
try:
    from advanced_animations import MaterialIcons as _MaterialIcons
    MaterialIcons = _MaterialIcons
except ImportError:
    MaterialIcons = MaterialIconsFallback
    print("⚠️ Usando fallback emoji per Material Icons")

'''
    
    # Salva fallback
    fallback_path = Path(__file__).parent / "material_icons_fallback.py"
    with open(fallback_path, 'w', encoding='utf-8') as f:
        f.write(fallback_code)
    
    print(f"✅ Fallback icons creato: {fallback_path}")


def setup_development_environment():
    """Setup ambiente di sviluppo completo"""
    print("🚀 Setup ambiente di sviluppo Monument Recognizer...")
    
    # Crea directory necessarie
    directories = ['fonts', 'cache', 'data', 'exports', 'temp']
    for dir_name in directories:
        dir_path = Path(__file__).parent / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"📁 Directory creata/verificata: {dir_path}")
    
    # Download font
    font_success = download_material_icons_font()
    
    # Test import moduli
    print("\n🔍 Test import moduli...")
    test_modules = [
        'monument_recognizer',
        'camera_interface',
        'user_system',
        'modern_ui',
        'advanced_animations',
        'enhanced_modern_ui',
        'intelligent_cache'
    ]
    
    failed_imports = []
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️ Moduli mancanti: {', '.join(failed_imports)}")
        print("💡 Assicurati che tutti i file siano presenti nella directory")
    else:
        print("\n🎉 Tutti i moduli importati correttamente!")
    
    # Test Kivy
    print("\n🎨 Test Kivy...")
    try:
        import kivy
        print(f"✅ Kivy {kivy.__version__}")
        
        from kivy.app import App
        from kivy.uix.label import Label
        print("✅ Widget Kivy base")
        
        from kivy.core.text import LabelBase
        print("✅ Font system Kivy")
        
    except ImportError as e:
        print(f"❌ Kivy non disponibile: {e}")
        print("💡 Installa Kivy: pip install kivy")
    
    print("\n✨ Setup completato!")
    return font_success and len(failed_imports) == 0


def create_launcher_script():
    """Crea script launcher per l'app"""
    launcher_code = '''#!/usr/bin/env python3
"""
Monument Recognizer Launcher
"""

import sys
import os
from pathlib import Path

# Aggiungi directory corrente al path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Avvia Monument Recognizer"""
    try:
        # Test setup
        print("🚀 Avvio Monument Recognizer...")
        
        # Import e avvio app
        from main import MainApp
        app = MainApp()
        app.run()
        
    except ImportError as e:
        print(f"❌ Errore import: {e}")
        print("💡 Esegui prima: python setup_fonts.py")
        return 1
        
    except Exception as e:
        print(f"❌ Errore avvio: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    launcher_path = Path(__file__).parent / "launcher.py"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    # Rendi eseguibile su Unix
    if os.name != 'nt':
        os.chmod(launcher_path, 0o755)
    
    print(f"🚀 Launcher creato: {launcher_path}")
    

if __name__ == "__main__":
    success = setup_development_environment()
    create_launcher_script()
    
    if success:
        print("\n🎉 Setup completato con successo!")
        print("🚀 Avvia l'app con: python launcher.py")
    else:
        print("\n⚠️ Setup completato con alcuni problemi")
        print("🔧 Verifica i messaggi di errore sopra")
