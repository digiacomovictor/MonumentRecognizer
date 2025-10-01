#!/usr/bin/env python3
"""
Script per Recuperare Log di Errore da GitHub Actions
Mostra gli ultimi errori delle build fallite
"""

import requests
import json
from datetime import datetime

def get_latest_failed_run():
    """Ottiene l'ultima build fallita"""
    api_url = "https://api.github.com/repos/digiacomovictor/MonumentRecognizer/actions/runs"
    
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            runs = data.get('workflow_runs', [])
            
            # Trova l'ultima build fallita
            for run in runs:
                if run.get('conclusion') == 'failure':
                    return run
            
            print("❌ Nessuna build fallita trovata")
            return None
        else:
            print(f"❌ Errore API: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Errore nel recupero run: {e}")
        return None

def get_job_logs(run_id):
    """Ottiene i log dei job per una specifica run"""
    jobs_url = f"https://api.github.com/repos/digiacomovictor/MonumentRecognizer/actions/runs/{run_id}/jobs"
    
    try:
        response = requests.get(jobs_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            
            for job in jobs:
                if job.get('conclusion') == 'failure':
                    print(f"🚨 JOB FALLITO: {job.get('name', 'Unknown')}")
                    print(f"🔗 URL: {job.get('html_url', 'N/A')}")
                    print(f"⏰ Inizio: {job.get('started_at', 'N/A')}")
                    print(f"⏰ Fine: {job.get('completed_at', 'N/A')}")
                    
                    # Mostra step falliti
                    steps = job.get('steps', [])
                    failed_steps = [s for s in steps if s.get('conclusion') == 'failure']
                    
                    if failed_steps:
                        print(f"\n📋 STEP FALLITI ({len(failed_steps)}):")
                        for step in failed_steps:
                            step_name = step.get('name', 'Unknown Step')
                            step_number = step.get('number', '?')
                            print(f"  {step_number}. ❌ {step_name}")
                            
                            # Se c'è log URL, proviamo a recuperarlo
                            if 'logs' in str(job):
                                print(f"     🔍 Per log dettagliati: {job.get('html_url')}")
                    
                    return job
            
            print("❌ Nessun job fallito trovato")
            return None
            
        else:
            print(f"❌ Errore recupero job: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Errore nel recupero job: {e}")
        return None

def analyze_common_failures(job_data):
    """Analizza errori comuni e suggerisce soluzioni"""
    print(f"\n🔍 === ANALISI ERRORI COMUNI ===")
    
    job_name = job_data.get('name', '').lower()
    steps = job_data.get('steps', [])
    
    # Errori comuni e soluzioni
    error_patterns = {
        'upload-artifact': {
            'description': 'Errore upload artifact (v3 deprecato)',
            'solution': 'Aggiornare a actions/upload-artifact@v4',
            'status': '✅ RISOLTO'
        },
        'buildozer': {
            'description': 'Errore buildozer durante build Android',
            'solution': 'Controllare dipendenze Android-compatibili',
            'status': '🔧 IN CORSO'
        },
        'java': {
            'description': 'Problemi configurazione Java/Android SDK',
            'solution': 'Verificare versione Java e Android SDK',
            'status': '⚠️ POSSIBILE'
        },
        'python': {
            'description': 'Import error o dipendenze Python',
            'solution': 'Rimuovere import non Android-compatibili',
            'status': '✅ PATCH APPLICATE'
        },
        'timeout': {
            'description': 'Timeout durante build (>90 min)',
            'solution': 'Prima build può richiedere tempo, riprova',
            'status': '⏳ NORMALE'
        }
    }
    
    # Controlla step per pattern di errore
    for step in steps:
        step_name = step.get('name', '').lower()
        if step.get('conclusion') == 'failure':
            print(f"\n❌ STEP FALLITO: {step.get('name')}")
            
            # Cerca pattern noti
            found_pattern = False
            for pattern, info in error_patterns.items():
                if pattern in step_name or pattern in str(step):
                    print(f"   🎯 Errore riconosciuto: {info['description']}")
                    print(f"   💡 Soluzione: {info['solution']}")
                    print(f"   📊 Status: {info['status']}")
                    found_pattern = True
                    break
            
            if not found_pattern:
                print(f"   ❓ Errore non riconosciuto - controlla log dettagliati")

def suggest_next_actions():
    """Suggerisce prossime azioni da intraprendere"""
    print(f"\n🚀 === PROSSIME AZIONI CONSIGLIATE ===")
    
    actions = [
        "1. 🌐 Apri GitHub Actions nel browser:",
        "   https://github.com/digiacomovictor/MonumentRecognizer/actions",
        "",
        "2. 🔍 Controlla log dettagliati:",
        "   • Clicca sull'ultima build fallita",
        "   • Espandi la sezione del job fallito",
        "   • Cerca linee con 'ERROR', 'FAILED', 'Exception'",
        "",
        "3. 📋 Copia le righe di errore specifiche:",
        "   • Ultimi 20-30 righe prima del fallimento",
        "   • Include stack trace se presente",
        "",
        "4. 🔧 Test locale (opzionale):",
        "   • python -m main (test import)",
        "   • buildozer android debug --verbose (se buildozer installato)",
        "",
        "5. 🆘 Se bloccato:",
        "   • Incolla le righe di errore specifiche",
        "   • Posso preparare fix mirati"
    ]
    
    for action in actions:
        print(action)

def main():
    """Funzione principale"""
    print("🏛️ === ANALISI LOG GITHUB ACTIONS ===\n")
    
    # Ottieni ultima run fallita
    print("🔍 Cercando ultima build fallita...")
    failed_run = get_latest_failed_run()
    
    if not failed_run:
        print("✅ Nessuna build fallita recente trovata!")
        return
    
    run_id = failed_run.get('id')
    run_number = failed_run.get('run_number')
    created_at = failed_run.get('created_at')
    html_url = failed_run.get('html_url')
    
    print(f"\n🚨 === BUILD FALLITA #{run_number} ===")
    print(f"🆔 Run ID: {run_id}")
    print(f"⏰ Creata: {created_at}")
    print(f"🔗 URL: {html_url}")
    
    # Ottieni dettagli job
    print(f"\n📋 Analizzando job falliti...")
    failed_job = get_job_logs(run_id)
    
    if failed_job:
        # Analizza errori comuni
        analyze_common_failures(failed_job)
    
    # Suggerimenti
    suggest_next_actions()
    
    print(f"\n🔗 Link diretto ai log: {html_url}")

if __name__ == "__main__":
    main()
