#!/usr/bin/env python3
"""
Script Diagnostico per Problemi GitHub Actions Build APK
Analizza configurazione e suggerisce soluzioni
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

def check_file_exists(file_path, description):
    """Controlla se un file esiste e ne mostra info"""
    if Path(file_path).exists():
        size = Path(file_path).stat().st_size
        print(f"✅ {description}: {file_path} ({size} bytes)")
        return True
    else:
        print(f"❌ {description}: {file_path} NON TROVATO!")
        return False

def analyze_buildozer_spec():
    """Analizza buildozer.spec per problemi comuni"""
    print("\n🔍 === ANALISI BUILDOZER.SPEC ===")
    
    if not check_file_exists("buildozer.spec", "File buildozer.spec"):
        return False
    
    with open("buildozer.spec", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # Problemi comuni da controllare
    issues = []
    
    # Requirements
    if "requirements = python3,kivy" in content:
        print("✅ Requirements base configurati")
        
        # Controlla dipendenze problematiche
        problematic_deps = ["opencv-python", "tensorflow", "torch", "numpy", "scipy"]
        for dep in problematic_deps:
            if dep in content.lower():
                issues.append(f"⚠️ Dipendenza problematica: {dep} (può causare build failure)")
    else:
        issues.append("❌ Requirements non trovati o malformattati")
    
    # Permissions
    if "android.permissions" in content:
        print("✅ Permessi Android configurati")
    else:
        issues.append("❌ Permessi Android mancanti")
    
    # API levels
    if "android.api = 31" in content or "android.api = 30" in content:
        print("✅ Android API configurato")
    else:
        issues.append("⚠️ Android API potrebbe essere troppo vecchio")
    
    # Architecture
    if "android.archs" in content:
        print("✅ Architetture Android specificate")
    else:
        issues.append("⚠️ Architetture Android non specificate")
    
    if issues:
        print(f"\n🚨 PROBLEMI RILEVATI ({len(issues)}):")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ Buildozer.spec sembra corretto!")
    
    return len(issues) == 0

def analyze_requirements():
    """Analizza requirements.txt per problemi Android"""
    print("\n📦 === ANALISI REQUIREMENTS.TXT ===")
    
    if not check_file_exists("requirements.txt", "File requirements.txt"):
        return False
    
    with open("requirements.txt", "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
    
    print(f"📋 Dipendenze trovate: {len(lines)}")
    
    # Dipendenze Android-compatibili
    android_friendly = ["kivy", "kivymd", "pillow", "requests", "plyer", "sqlite3"]
    problematic = ["opencv-python", "tensorflow", "torch", "numpy", "scipy", "matplotlib", "pandas", "folium", "google-cloud"]
    
    issues = []
    good_deps = []
    bad_deps = []
    
    for line in lines:
        dep_name = line.split('==')[0].split('>=')[0].split('<=')[0].lower()
        
        if any(good in dep_name for good in android_friendly):
            good_deps.append(line)
        elif any(bad in dep_name for bad in problematic):
            bad_deps.append(line)
            issues.append(f"⚠️ {line} - Problematico su Android")
    
    print(f"\n✅ Dipendenze OK: {len(good_deps)}")
    for dep in good_deps[:5]:  # Mostra prime 5
        print(f"  ✅ {dep}")
    if len(good_deps) > 5:
        print(f"  ... e {len(good_deps)-5} altre")
    
    if bad_deps:
        print(f"\n⚠️ Dipendenze Problematiche: {len(bad_deps)}")
        for dep in bad_deps:
            print(f"  ❌ {dep}")
    
    return len(bad_deps) == 0

def check_github_workflow():
    """Controlla workflow GitHub Actions"""
    print("\n🚀 === ANALISI GITHUB ACTIONS ===")
    
    workflow_path = ".github/workflows/android-build.yml"
    if not check_file_exists(workflow_path, "Workflow GitHub Actions"):
        return False
    
    with open(workflow_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Controlla componenti chiave
    checks = [
        ("runs-on: ubuntu-latest", "Runner Ubuntu"),
        ("buildozer android debug", "Comando buildozer"),
        ("uses: actions/upload-artifact", "Upload artifacts"),
        ("java-version: '11'", "Java 11 setup"),
        ("python-version:", "Python setup")
    ]
    
    issues = []
    for check, description in checks:
        if check in content:
            print(f"✅ {description}")
        else:
            issues.append(f"❌ {description} - Non trovato")
    
    if issues:
        print(f"\n🚨 PROBLEMI WORKFLOW ({len(issues)}):")
        for issue in issues:
            print(f"  {issue}")
    
    return len(issues) == 0

def get_github_actions_status():
    """Controlla status delle GitHub Actions (se possibile)"""
    print("\n📊 === STATUS GITHUB ACTIONS ===")
    
    repo_url = "https://github.com/digiacomovictor/MonumentRecognizer"
    actions_url = f"{repo_url}/actions"
    
    print(f"🔗 Repository: {repo_url}")
    print(f"🔗 Actions: {actions_url}")
    
    # Prova a fare una richiesta basic alle API GitHub (senza auth)
    try:
        api_url = "https://api.github.com/repos/digiacomovictor/MonumentRecognizer/actions/runs"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            runs = data.get('workflow_runs', [])
            
            if runs:
                print(f"\n📈 Ultime {min(3, len(runs))} build trovate:")
                
                for i, run in enumerate(runs[:3]):
                    status = run.get('status', 'unknown')
                    conclusion = run.get('conclusion', 'unknown')
                    created_at = run.get('created_at', '')
                    workflow_name = run.get('name', 'Unknown')
                    
                    # Emoji per status
                    status_emoji = {
                        'completed': '✅' if conclusion == 'success' else '❌',
                        'in_progress': '🔄',
                        'queued': '⏳'
                    }.get(status, '❓')
                    
                    print(f"  {i+1}. {status_emoji} {workflow_name}")
                    print(f"     Status: {status} | Conclusion: {conclusion}")
                    print(f"     Creata: {created_at}")
                    print(f"     URL: {run.get('html_url', 'N/A')}")
                    print()
                
                # Controlla se ci sono build fallite
                failed_runs = [r for r in runs if r.get('conclusion') == 'failure']
                if failed_runs:
                    print(f"🚨 Trovate {len(failed_runs)} build FALLITE!")
                    latest_failed = failed_runs[0]
                    print(f"   Ultima build fallita: {latest_failed.get('html_url')}")
                    
                    return False
                else:
                    success_runs = [r for r in runs if r.get('conclusion') == 'success']
                    if success_runs:
                        print(f"✅ Trovate {len(success_runs)} build RIUSCITE!")
                        return True
            else:
                print("⚠️ Nessuna build trovata - potrebbe non essere mai stata eseguita")
                
        elif response.status_code == 404:
            print("❌ Repository non trovato o privato")
        else:
            print(f"⚠️ Errore API GitHub: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"⚠️ Impossibile contattare GitHub API: {e}")
    
    print(f"\n💡 Per vedere i log dettagliati:")
    print(f"   1. Vai su {actions_url}")
    print(f"   2. Clicca sulla build più recente")
    print(f"   3. Espandi i log per vedere l'errore specifico")
    
    return None

def suggest_solutions():
    """Suggerisce soluzioni per problemi comuni"""
    print("\n💡 === SOLUZIONI COMUNI ===")
    
    solutions = [
        "🔧 DIPENDENZE PROBLEMATICHE:",
        "   • Rimuovi opencv-python, tensorflow, numpy da requirements.txt",
        "   • Usa solo: kivy, kivymd, pillow, requests, plyer",
        "",
        "⚙️ BUILDOZER.SPEC:",
        "   • Verifica che requirements sia: python3,kivy==2.1.0,kivymd,pillow,requests,plyer",
        "   • Controlla android.api = 31 e android.minapi = 21",
        "",
        "🐍 MAIN.PY ANDROID-READY:",
        "   • Assicurati che main.py importi solo librerie Android-compatibili",
        "   • Usa try/except per import opzionali",
        "",
        "☁️ GITHUB ACTIONS:",
        "   • Repository deve essere pubblico per Actions gratuito",
        "   • Prima build richiede ~60 minuti (normale)",
        "   • Build successive ~15 minuti con cache",
        "",
        "🔍 DEBUG:",
        "   • Vai su github.com/digiacomovictor/MonumentRecognizer/actions",
        "   • Clicca sulla build fallita",
        "   • Cerca errori nei log (di solito nella sezione 'Build APK')",
        "",
        "🚀 BUILD MANUALE:",
        "   • Se tutto fallisce, prova: git push --force-with-lease",
        "   • Oppure fai un nuovo commit: git commit --allow-empty -m 'Trigger build'"
    ]
    
    for solution in solutions:
        print(solution)

def create_fixed_files():
    """Crea versioni corrette dei file problematici"""
    print("\n🔧 === CREAZIONE FILE CORRETTI ===")
    
    # Requirements.txt Android-only
    android_requirements = """# Requirements ottimizzati per Android build
# Solo dipendenze Android-compatibili

kivy==2.1.0
kivymd>=1.0.0
Pillow>=9.0.0
requests>=2.25.0
plyer>=2.0.0

# Note: Rimosse tutte le dipendenze problematiche per Android
# - opencv-python (causa errori di build)
# - tensorflow/torch (troppo pesanti)
# - numpy/scipy (problemi con NDK)
# - matplotlib/plotly (dipendenze web)
# - folium (dipende da browser)
"""
    
    try:
        with open("requirements_android.txt", "w", encoding="utf-8") as f:
            f.write(android_requirements)
        print("✅ Creato requirements_android.txt ottimizzato")
    except Exception as e:
        print(f"❌ Errore nella creazione requirements_android.txt: {e}")
    
    # Main.py Android-ready snippet
    android_main_snippet = '''"""
main.py Android-Ready - Snippet di esempio
Usa import condizionali per evitare errori su Android
"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# Import condizionali per Android
try:
    from push_notifications import PushNotificationManager
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

try:
    from gamification import GamificationManager  
    GAMIFICATION_AVAILABLE = True
except ImportError:
    GAMIFICATION_AVAILABLE = False

class MonumentRecognizerApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Title
        title = Label(
            text='🏛️ Monument Recognizer\\nAndroid Ready!',
            font_size=24,
            halign='center'
        )
        layout.add_widget(title)
        
        # Status sistemi
        status_text = "Sistemi disponibili:\\n"
        if NOTIFICATIONS_AVAILABLE:
            status_text += "✅ Sistema Notifiche Push\\n"
        if GAMIFICATION_AVAILABLE:
            status_text += "✅ Sistema Gamification\\n"
        
        status_label = Label(text=status_text, font_size=14)
        layout.add_widget(status_label)
        
        # Test button
        test_btn = Button(text='🧪 Test Funzionalità', size_hint_y=None, height=50)
        test_btn.bind(on_press=self.test_features)
        layout.add_widget(test_btn)
        
        return layout
    
    def test_features(self, *args):
        print("🧪 Test funzionalità Android...")
        
        if NOTIFICATIONS_AVAILABLE:
            try:
                # Test notifiche
                manager = PushNotificationManager()
                notif_id = manager.create_notification(
                    title="📱 Test Android",
                    body="Sistema notifiche funzionante!",
                    user_id="android_test"
                )
                print(f"✅ Notifica test creata: {notif_id}")
            except Exception as e:
                print(f"⚠️ Errore test notifiche: {e}")
        
        print("✅ Test Android completato!")

if __name__ == '__main__':
    MonumentRecognizerApp().run()
'''
    
    try:
        with open("main_android_ready.py", "w", encoding="utf-8") as f:
            f.write(android_main_snippet)
        print("✅ Creato main_android_ready.py come esempio")
    except Exception as e:
        print(f"❌ Errore nella creazione main_android_ready.py: {e}")

def main():
    """Funzione principale diagnostica"""
    print("🏛️ === DIAGNOSI GITHUB ACTIONS BUILD APK ===")
    print("Analizzando configurazione e problemi comuni...\n")
    
    all_good = True
    
    # Controlla file essenziali
    essential_files = [
        ("main.py", "File principale app"),
        ("buildozer.spec", "Configurazione build Android"),
        ("requirements.txt", "Dipendenze Python"),
        (".github/workflows/android-build.yml", "Workflow GitHub Actions")
    ]
    
    print("📁 === CONTROLLO FILE ESSENZIALI ===")
    for file_path, desc in essential_files:
        if not check_file_exists(file_path, desc):
            all_good = False
    
    # Analisi dettagliata
    buildozer_ok = analyze_buildozer_spec()
    requirements_ok = analyze_requirements()
    workflow_ok = check_github_workflow()
    
    # Status GitHub Actions
    github_status = get_github_actions_status()
    
    # Riepilogo
    print(f"\n📊 === RIEPILOGO DIAGNOSI ===")
    print(f"File essenziali: {'✅' if all_good else '❌'}")
    print(f"Buildozer.spec: {'✅' if buildozer_ok else '❌'}")
    print(f"Requirements.txt: {'✅' if requirements_ok else '❌'}")
    print(f"GitHub Workflow: {'✅' if workflow_ok else '❌'}")
    print(f"GitHub Actions: {'✅' if github_status else '❌' if github_status is False else '❓'}")
    
    # Suggerimenti
    if not all([buildozer_ok, requirements_ok, workflow_ok]):
        suggest_solutions()
        create_fixed_files()
        
        print(f"\n🔧 === AZIONI CONSIGLIATE ===")
        print("1. Usa requirements_android.txt per dipendenze corrette")
        print("2. Verifica main.py usi import condizionali") 
        print("3. Controlla buildozer.spec con requirements ottimizzati")
        print("4. Fai nuovo push per triggerare build")
        print("5. Monitora i log su GitHub Actions")
    else:
        print(f"\n🎉 === CONFIGURAZIONE OK ===")
        print("La configurazione sembra corretta!")
        print("Se la build fallisce ancora, controlla i log GitHub Actions per errori specifici")
    
    print(f"\n🔗 Link utili:")
    print(f"   GitHub Actions: https://github.com/digiacomovictor/MonumentRecognizer/actions")
    print(f"   Repository: https://github.com/digiacomovictor/MonumentRecognizer")

if __name__ == "__main__":
    main()
