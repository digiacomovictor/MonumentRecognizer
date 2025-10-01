#!/usr/bin/env python3
"""
Project Status Monitor per Monument Recognizer
Mostra stato completo del progetto e prossimi passi
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

def check_local_setup():
    """Controlla setup locale"""
    print("🏗️ === STATUS SETUP LOCALE ===")
    
    # Files essenziali
    essential_files = {
        'main.py': 'File principale app',
        'buildozer.spec': 'Config build Android',
        'requirements.txt': 'Dipendenze Python',
        '.github/workflows/android-build.yml': 'Workflow principale',
        '.github/workflows/quick-test.yml': 'Test rapido',
        '.gitignore': 'Git ignore file'
    }
    
    all_good = True
    for file, desc in essential_files.items():
        if Path(file).exists():
            size = Path(file).stat().st_size
            print(f"✅ {file} - {desc} ({size} bytes)")
        else:
            print(f"❌ {file} - {desc} MANCANTE!")
            all_good = False
    
    # Scripts di supporto
    support_scripts = {
        'diagnose_github_build.py': 'Diagnostica problemi build',
        'monitor_build.py': 'Monitor build in tempo reale',
        'get_build_logs.py': 'Estrae log di errore',
        'apply_android_patches.py': 'Gestisce patch Android',
        'project_status.py': 'Questo script'
    }
    
    print(f"\n🛠️ Script di Supporto:")
    for script, desc in support_scripts.items():
        if Path(script).exists():
            print(f"✅ {script} - {desc}")
        else:
            print(f"❌ {script} - {desc}")
    
    # File backup
    backup_files = [f for f in os.listdir('.') if f.endswith('.desktop_backup')]
    if backup_files:
        print(f"\n💾 File Backup Trovati ({len(backup_files)}):")
        for backup in backup_files:
            print(f"  📁 {backup}")
    
    return all_good

def check_github_status():
    """Controlla status GitHub Actions"""
    print(f"\n🚀 === STATUS GITHUB ACTIONS ===")
    
    try:
        api_url = "https://api.github.com/repos/digiacomovictor/MonumentRecognizer/actions/runs"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            runs = data.get('workflow_runs', [])
            
            if runs:
                print(f"📊 Ultime 5 build:")
                
                for i, run in enumerate(runs[:5]):
                    status = run.get('status', 'unknown')
                    conclusion = run.get('conclusion', 'none')
                    workflow_name = run.get('name', 'Unknown')
                    run_number = run.get('run_number', '?')
                    created_at = run.get('created_at', '')[:10]  # Solo data
                    
                    # Emoji status
                    if status == 'in_progress':
                        emoji = "🔄"
                    elif conclusion == 'success':
                        emoji = "✅"
                    elif conclusion == 'failure':
                        emoji = "❌"
                    else:
                        emoji = "❓"
                    
                    print(f"  {i+1}. {emoji} #{run_number} - {workflow_name} ({created_at})")
                
                # Statistiche
                total_runs = len(runs)
                success_runs = len([r for r in runs if r.get('conclusion') == 'success'])
                failed_runs = len([r for r in runs if r.get('conclusion') == 'failure'])
                in_progress = len([r for r in runs if r.get('status') == 'in_progress'])
                
                print(f"\n📈 Statistiche Build:")
                print(f"  📊 Totali: {total_runs}")
                print(f"  ✅ Successo: {success_runs}")
                print(f"  ❌ Fallite: {failed_runs}")
                if in_progress > 0:
                    print(f"  🔄 In corso: {in_progress}")
                
                return success_runs > 0
            else:
                print("❌ Nessuna build trovata")
                return False
        else:
            print(f"⚠️ Errore API GitHub: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Errore connessione: {e}")
        return None

def analyze_current_issues():
    """Analizza problemi correnti e soluzioni"""
    print(f"\n🔍 === ANALISI PROBLEMI CORRENTI ===")
    
    known_issues = [
        {
            'issue': 'Upload Artifact v3 deprecato',
            'status': '✅ RISOLTO',
            'action': 'Aggiornato a v4 in tutti i workflow'
        },
        {
            'issue': 'Dipendenze non Android-compatibili',
            'status': '✅ RISOLTO', 
            'action': 'Patch applicate: rimosso OpenCV, matplotlib, folium'
        },
        {
            'issue': 'Workflow duplicato con errori',
            'status': '✅ RISOLTO',
            'action': 'Rimosso build_apk.yml obsoleto'
        },
        {
            'issue': 'Buildozer timeout durante SDK download',
            'status': '🔧 MIGLIORATO',
            'action': 'Aggiunto retry logic e timeout estesi'
        },
        {
            'issue': 'Cache buildozer non ottimizzata',
            'status': '💾 IN CORSO',
            'action': 'Sistema cache implementato nel workflow'
        }
    ]
    
    for issue_data in known_issues:
        status_color = issue_data['status']
        print(f"{status_color} {issue_data['issue']}")
        print(f"    💡 {issue_data['action']}")

def suggest_next_steps():
    """Suggerisce prossimi passi"""
    print(f"\n🎯 === PROSSIMI PASSI CONSIGLIATI ===")
    
    steps = [
        {
            'priority': '🔥 ALTA',
            'action': 'Test Build Rapido',
            'details': [
                '1. Vai su GitHub Actions',
                '2. Esegui "🚀 Quick Android Test" workflow',
                '3. Verifica setup base senza download SDK'
            ]
        },
        {
            'priority': '⚡ MEDIA',
            'action': 'Build Completa con Retry',
            'details': [
                '1. Se quick test OK, esegui workflow principale',
                '2. Nuovo retry logic dovrebbe gestire timeout',
                '3. Monitor con: python monitor_build.py'
            ]
        },
        {
            'priority': '🔧 BASSA',
            'action': 'Ottimizzazioni Avanzate',
            'details': [
                '1. Pre-cache Android SDK se build fallisce ancora',
                '2. Split build in multiple stage',
                '3. Setup Android SDK separato'
            ]
        }
    ]
    
    for step in steps:
        print(f"\n{step['priority']} - {step['action']}:")
        for detail in step['details']:
            print(f"   {detail}")

def show_useful_commands():
    """Mostra comandi utili"""
    print(f"\n💻 === COMANDI UTILI ===")
    
    commands = {
        'Monitor build in tempo reale': 'python monitor_build.py',
        'Diagnosi problemi build': 'python diagnose_github_build.py', 
        'Analizza log errori': 'python get_build_logs.py',
        'Applica patch Android': 'python apply_android_patches.py',
        'Status progetto completo': 'python project_status.py',
        'Test import locali': 'python -c "import main; print(\'OK\')"'
    }
    
    for desc, cmd in commands.items():
        print(f"🔹 {desc}:")
        print(f"   {cmd}")

def main():
    """Funzione principale"""
    print("🏛️ === MONUMENT RECOGNIZER - PROJECT STATUS ===")
    print(f"📅 Aggiornato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check setup locale
    local_ok = check_local_setup()
    
    # Check GitHub
    github_ok = check_github_status()
    
    # Analisi problemi
    analyze_current_issues()
    
    # Prossimi passi
    suggest_next_steps()
    
    # Comandi utili
    show_useful_commands()
    
    # Summary finale
    print(f"\n📊 === RIEPILOGO FINALE ===")
    print(f"🏗️ Setup Locale: {'✅ OK' if local_ok else '❌ PROBLEMI'}")
    
    if github_ok is True:
        print(f"🚀 GitHub Actions: ✅ ALMENO 1 BUILD RIUSCITA!")
    elif github_ok is False:
        print(f"🚀 GitHub Actions: ❌ Tutte le build fallite")
    else:
        print(f"🚀 GitHub Actions: ❓ Non verificabile")
    
    print(f"\n🔗 Link Importanti:")
    print(f"   📱 GitHub Actions: https://github.com/digiacomovictor/MonumentRecognizer/actions")
    print(f"   📂 Repository: https://github.com/digiacomovictor/MonumentRecognizer")
    print(f"   📋 Issues: https://github.com/digiacomovictor/MonumentRecognizer/issues")
    
    if github_ok is True:
        print(f"\n🎉 CONGRATULAZIONI! Il progetto è configurato correttamente!")
        print(f"💡 Scarica l'APK dalla sezione Artifacts delle build riuscite!")
    else:
        print(f"\n🔧 Il progetto è quasi pronto - serve solo risolvere il download Android SDK")
        print(f"💡 Prova il Quick Test workflow per debug veloce!")

if __name__ == "__main__":
    main()
