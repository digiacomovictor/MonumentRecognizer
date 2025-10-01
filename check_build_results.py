#!/usr/bin/env python3
"""
Script di analisi rapido per controllare i risultati delle build Android
"""

import requests
import time
from datetime import datetime

def check_build_status():
    """Controllo rapido dello status build con retry per rate limiting"""
    
    owner = "digiacomovictor"
    repo = "MonumentRecognizer" 
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Build-Status-Checker/1.0"
    }
    
    print("🔍 CONTROLLO RISULTATI BUILD ANDROID")
    print("="*50)
    
    # URL specifici che vogliamo controllare
    runs_to_check = [
        ("🆕 Android Build - NDK Fixed", "18178876141"),
        ("🔴 Build Android APK", "18178876131"),
    ]
    
    for name, run_id in runs_to_check:
        print(f"\n🏗️  {name}")
        print(f"   Run ID: {run_id}")
        
        try:
            # Prova a ottenere info sul run specifico
            url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                run_data = response.json()
                
                status = run_data.get('status', 'unknown')
                conclusion = run_data.get('conclusion', 'none')
                
                # Emoji per status
                if status == 'completed':
                    if conclusion == 'success':
                        emoji = "✅"
                        result = "SUCCESSO"
                    elif conclusion == 'failure':
                        emoji = "❌"
                        result = "FALLITO"
                    elif conclusion == 'cancelled':
                        emoji = "🚫"
                        result = "CANCELLATO"
                    else:
                        emoji = "⚠️"
                        result = f"COMPLETATO ({conclusion})"
                elif status == 'in_progress':
                    emoji = "🔄"
                    result = "IN CORSO"
                elif status == 'queued':
                    emoji = "⏳"
                    result = "IN CODA"
                else:
                    emoji = "❓"
                    result = f"SCONOSCIUTO ({status})"
                
                # Calcola durata
                created_at = datetime.fromisoformat(run_data['created_at'].replace('Z', '+00:00'))
                if status == 'completed' and run_data.get('updated_at'):
                    updated_at = datetime.fromisoformat(run_data['updated_at'].replace('Z', '+00:00'))
                    duration = int((updated_at - created_at).total_seconds())
                else:
                    duration = int((datetime.now(created_at.tzinfo) - created_at).total_seconds())
                
                duration_str = f"{duration//60}m {duration%60}s" if duration >= 60 else f"{duration}s"
                
                print(f"   {emoji} Status: {result}")
                print(f"   ⏱️  Durata: {duration_str}")
                print(f"   📅 Iniziato: {created_at.strftime('%H:%M:%S')}")
                print(f"   🔗 URL: https://github.com/{owner}/{repo}/actions/runs/{run_id}")
                
                # Info aggiuntive se disponibili
                if run_data.get('head_commit'):
                    commit_msg = run_data['head_commit']['message'][:60] + "..." if len(run_data['head_commit']['message']) > 60 else run_data['head_commit']['message']
                    print(f"   📝 Commit: {commit_msg}")
                
            elif response.status_code == 403:
                print(f"   ⚠️  Rate limit GitHub API - Controlla manualmente:")
                print(f"   🔗 https://github.com/{owner}/{repo}/actions/runs/{run_id}")
            else:
                print(f"   ❌ Errore API: {response.status_code}")
                print(f"   🔗 https://github.com/{owner}/{repo}/actions/runs/{run_id}")
                
        except Exception as e:
            print(f"   ❌ Errore connessione: {e}")
            print(f"   🔗 https://github.com/{owner}/{repo}/actions/runs/{run_id}")
    
    print(f"\n{'='*50}")
    print("📋 RIASSUNTO:")
    print("1. Controlla i link sopra per i dettagli completi")
    print("2. Se il nuovo workflow (NDK Fixed) è riuscito, abbiamo risolto il problema!")
    print("3. Se è ancora in corso, aspettiamo il completamento")
    print("4. I log sono automaticamente salvati come artifacts")
    
    print(f"\n🔄 Per ricontrollare tra qualche minuto:")
    print("python check_build_results.py")

if __name__ == "__main__":
    check_build_status()
