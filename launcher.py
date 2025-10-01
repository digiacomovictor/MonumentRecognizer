#!/usr/bin/env python3
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
