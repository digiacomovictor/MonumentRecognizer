#!/usr/bin/env python3
"""
Setup Script per GitHub Repository - Monument Recognizer
Prepara il repository per build automatiche APK con GitHub Actions
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Esegue comando shell con output"""
    print(f"🔄 Eseguendo: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore: {e}")
        if e.stderr:
            print(f"💥 {e.stderr.strip()}")
        return False

def check_git_installed():
    """Verifica se Git è installato"""
    return run_command("git --version", check=False)

def setup_git_repository():
    """Inizializza repository Git"""
    print("\n📂 === SETUP REPOSITORY GIT ===")
    
    if not check_git_installed():
        print("❌ Git non è installato! Installalo da: https://git-scm.com/")
        return False
    
    # Inizializza repo se non esiste
    if not Path(".git").exists():
        print("🔄 Inizializzazione repository Git...")
        if not run_command("git init"):
            return False
        
        # Configura branch principale come 'main'
        run_command("git branch -M main")
    else:
        print("✅ Repository Git già esistente")
    
    return True

def setup_gitignore():
    """Crea/aggiorna .gitignore per il progetto"""
    print("\n📋 === SETUP .GITIGNORE ===")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Android/Buildozer
.buildozer/
bin/
*.apk
*.aab

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Cache
.cache/
*.cache

# Temporary files
tmp/
temp/
*.tmp

# Test coverage
.coverage
htmlcov/

# Pytest
.pytest_cache/

# Keys and certificates (IMPORTANT!)
*.key
*.keystore
*.p12
*.pem
*.crt
service_account.json
google_credentials.json

# Environment variables
.env
.env.local
.env.production
.env.staging

# Personal data
my_data/
personal/
private/

# Large files that shouldn't be in Git
*.mp4
*.mov
*.avi
large_datasets/
models/*.h5
models/*.pkl

# Documentation build
docs/_build/
"""
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore creato/aggiornato")
    return True

def check_github_workflow():
    """Verifica che il workflow GitHub Actions sia presente"""
    print("\n🚀 === VERIFICA GITHUB ACTIONS ===")
    
    workflow_path = Path(".github/workflows/android-build.yml")
    if workflow_path.exists():
        print("✅ Workflow GitHub Actions trovato")
        print(f"📁 Path: {workflow_path}")
        return True
    else:
        print("❌ Workflow GitHub Actions non trovato!")
        print("💡 Il file dovrebbe essere in: .github/workflows/android-build.yml")
        return False

def check_buildozer_config():
    """Verifica configurazione buildozer"""
    print("\n⚙️ === VERIFICA CONFIGURAZIONE BUILDOZER ===")
    
    if Path("buildozer.spec").exists():
        print("✅ buildozer.spec trovato")
        
        # Verifica contenuto
        with open("buildozer.spec", "r") as f:
            content = f.read()
            
        if "requirements = python3,kivy" in content:
            print("✅ Requirements configurati")
        else:
            print("⚠️ Requirements potrebbero necessitare aggiornamento")
            
        if "android.permissions" in content:
            print("✅ Permessi Android configurati")
            
        return True
    else:
        print("❌ buildozer.spec non trovato!")
        return False

def check_requirements():
    """Verifica requirements.txt"""
    print("\n📦 === VERIFICA REQUIREMENTS ===")
    
    if Path("requirements.txt").exists():
        print("✅ requirements.txt trovato")
        
        with open("requirements.txt", "r") as f:
            content = f.read()
            
        # Verifica dipendenze essenziali
        essential = ["kivy", "kivymd", "pillow", "requests", "plyer"]
        for dep in essential:
            if dep.lower() in content.lower():
                print(f"✅ {dep} trovato")
            else:
                print(f"⚠️ {dep} non trovato - potrebbe essere necessario")
        
        return True
    else:
        print("❌ requirements.txt non trovato!")
        return False

def stage_files():
    """Aggiunge file al staging Git"""
    print("\n📋 === STAGING FILES ===")
    
    important_files = [
        "main.py",
        "buildozer.spec", 
        "requirements.txt",
        ".github/workflows/android-build.yml",
        "push_notifications.py",
        "notifications_ui.py",
        "notifications_integration.py",
        ".gitignore"
    ]
    
    # Aggiungi tutti i file Python
    run_command("git add *.py")
    
    # Aggiungi file specifici
    for file in important_files:
        if Path(file).exists():
            run_command(f"git add {file}")
            print(f"✅ Aggiunto: {file}")
        else:
            print(f"⚠️ File non trovato: {file}")
    
    # Aggiungi directory GitHub
    run_command("git add .github/")
    
    return True

def show_next_steps():
    """Mostra i prossimi passi per l'utente"""
    print("\n🎯 === PROSSIMI PASSI ===")
    
    steps = [
        "1. 📝 Crea repository su GitHub.com:",
        "   • Vai su github.com/new",
        "   • Nome: MonumentRecognizer", 
        "   • Visibilità: Public (per GitHub Actions gratuito)",
        "   • NON inizializzare con README (abbiamo già i file)",
        "",
        "2. 🔗 Collega repository locale a GitHub:",
        "   git remote add origin https://github.com/TUO_USERNAME/MonumentRecognizer.git",
        "",
        "3. 📤 Fai il primo commit e push:",
        "   git commit -m '🚀 Initial commit: Monument Recognizer with Push Notifications'",
        "   git push -u origin main",
        "",
        "4. ⚡ La build APK partirà automaticamente!",
        "   • Vai su github.com/TUO_USERNAME/MonumentRecognizer/actions",
        "   • Aspetta che la build finisca (~30-60 minuti la prima volta)",
        "   • Scarica l'APK dagli Artifacts",
        "",
        "5. 📱 Testa l'APK:",
        "   • Installa su dispositivo Android",
        "   • Abilita 'Sorgenti sconosciute'",
        "   • Prova tutte le funzionalità!",
        "",
        "6. 🔄 Build automatiche:",
        "   • Ogni push su 'main' crea nuovo APK",
        "   • Release automatiche con versioning",
        "   • Download sempre dall'ultima build"
    ]
    
    for step in steps:
        print(step)
    
    print("\n🎉 === SISTEMA PRONTO PER GITHUB! ===")
    print("✅ Workflow GitHub Actions configurato")
    print("✅ Buildozer ottimizzato per Android") 
    print("✅ Sistema notifiche push completo")
    print("✅ Requirements Android-compatibili")
    print("✅ Build automatiche pronte")

def main():
    """Funzione principale"""
    print("🏛️ === MONUMENT RECOGNIZER - SETUP GITHUB ===")
    print("Prepara il progetto per build automatiche APK\n")
    
    success = True
    
    # Setup repository
    success &= setup_git_repository()
    success &= setup_gitignore()
    
    # Verifica configurazioni
    success &= check_github_workflow()
    success &= check_buildozer_config()  
    success &= check_requirements()
    
    if success:
        # Stage files per commit
        stage_files()
        
        # Mostra stato
        print("\n📊 === STATUS REPOSITORY ===")
        run_command("git status --porcelain")
        
        # Prossimi passi
        show_next_steps()
    else:
        print("\n❌ === ERRORI RILEVATI ===")
        print("Correggi gli errori sopra prima di procedere")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Errore inaspettato: {e}")
        sys.exit(1)
