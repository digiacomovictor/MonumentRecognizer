#!/usr/bin/env python3
"""
Script per testare il nuovo workflow Android Build ottimizzato
Triggera il workflow e monitora l'esecuzione
"""

import requests
import time
import json
import sys
import subprocess

def trigger_workflow(owner, repo, token, workflow_name="android-build-fixed.yml"):
    """Triggera manualmente il workflow"""
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
        "User-Agent": "Android-Build-Tester/1.0"
    }
    
    # Triggera workflow_dispatch
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_name}/dispatches"
    
    data = {
        "ref": "main"  # o "master" se usi master come branch principale
    }
    
    print(f"🚀 Triggering workflow: {workflow_name}")
    print(f"   Repository: {owner}/{repo}")
    print(f"   URL: {url}")
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        print("✅ Workflow triggered successfully!")
        return True
    else:
        print(f"❌ Failed to trigger workflow: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def main():
    print("🧪 ANDROID BUILD TEST SUITE")
    print("="*50)
    
    # Configurazione - modifica questi valori
    OWNER = "YOUR_GITHUB_USERNAME"  # Sostituisci con il tuo username GitHub
    REPO = "MonumentRecognizer"
    TOKEN = None  # Sostituisci con il tuo GitHub token se disponibile
    
    if not TOKEN:
        print("⚠️  GitHub token non configurato!")
        print("   Per triggerare workflow automaticamente, configura il token.")
        print("   Puoi comunque eseguire il workflow manualmente da GitHub.")
        
        # Prova a ottenere informazioni senza token
        try:
            response = requests.get(f"https://api.github.com/repos/{OWNER}/{REPO}")
            if response.status_code == 200:
                repo_info = response.json()
                print(f"✅ Repository trovato: {repo_info['full_name']}")
                print(f"   Default branch: {repo_info['default_branch']}")
            else:
                print(f"❌ Repository non trovato o non accessibile: {response.status_code}")
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
        
        print("\n📋 ISTRUZIONI MANUALI:")
        print("1. Vai su GitHub nella tab 'Actions' del repository")
        print("2. Seleziona il workflow 'Android Build - NDK Fixed'")
        print("3. Clicca 'Run workflow' e conferma")
        print("4. Usa il monitor script per seguire il progresso:")
        print(f"   python monitor_android_build.py --owner {OWNER} --repo {REPO} --watch")
        
        return
    
    # Se abbiamo il token, triggera automaticamente
    success = trigger_workflow(OWNER, REPO, TOKEN)
    
    if success:
        print("\n📊 Per monitorare l'esecuzione, usa:")
        print(f"python monitor_android_build.py --owner {OWNER} --repo {REPO} --token {TOKEN} --watch")
        
        # Avvia automaticamente il monitoring se richiesto
        user_input = input("\n❓ Vuoi avviare il monitoraggio automaticamente? (y/n): ")
        if user_input.lower() in ['y', 'yes', 's', 'si']:
            try:
                subprocess.run([
                    sys.executable, "monitor_android_build.py",
                    "--owner", OWNER,
                    "--repo", REPO,
                    "--token", TOKEN,
                    "--watch"
                ])
            except KeyboardInterrupt:
                print("\n👋 Monitoring interrotto")
            except FileNotFoundError:
                print("❌ Script monitor_android_build.py non trovato nella directory corrente")

if __name__ == "__main__":
    main()
