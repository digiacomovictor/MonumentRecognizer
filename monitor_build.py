#!/usr/bin/env python3
"""
Script per Monitorare GitHub Actions Build APK in tempo reale
Controlla status e mostra log degli errori se necessario
"""

import requests
import time
import json
from datetime import datetime

def check_latest_build():
    """Controlla l'ultima build e ne mostra lo status"""
    
    api_url = "https://api.github.com/repos/digiacomovictor/MonumentRecognizer/actions/runs"
    
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            runs = data.get('workflow_runs', [])
            
            if runs:
                latest = runs[0]  # La più recente
                
                status = latest.get('status', 'unknown')
                conclusion = latest.get('conclusion', 'none')
                created_at = latest.get('created_at', '')
                workflow_name = latest.get('name', 'Unknown')
                run_number = latest.get('run_number', '?')
                html_url = latest.get('html_url', '')
                
                # Emoji per status
                if status == 'in_progress':
                    emoji = "🔄"
                elif status == 'queued':
                    emoji = "⏳"
                elif status == 'completed':
                    if conclusion == 'success':
                        emoji = "✅"
                    elif conclusion == 'failure':
                        emoji = "❌"
                    elif conclusion == 'cancelled':
                        emoji = "⏹️"
                    else:
                        emoji = "❓"
                else:
                    emoji = "❓"
                
                print(f"\n🏛️ === BUILD #{run_number} ===")
                print(f"{emoji} {workflow_name}")
                print(f"📊 Status: {status}")
                if conclusion != 'none':
                    print(f"🎯 Risultato: {conclusion}")
                print(f"⏰ Creata: {created_at}")
                print(f"🔗 URL: {html_url}")
                
                # Se è in corso, calcolpiamo il tempo trascorso
                if status == 'in_progress':
                    try:
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        now = datetime.now(created_time.tzinfo)
                        elapsed = now - created_time
                        elapsed_minutes = int(elapsed.total_seconds() / 60)
                        
                        print(f"⏱️ Tempo trascorso: {elapsed_minutes} minuti")
                        
                        if elapsed_minutes > 60:
                            print("⚠️ Build molto lunga - potrebbe esserci un problema")
                        elif elapsed_minutes > 30:
                            print("⏳ Build normale - la prima build può richiedere 60+ minuti")
                        else:
                            print("🚀 Build appena iniziata")
                            
                    except:
                        print("⏱️ Tempo trascorso: non calcolabile")
                
                # Se fallita, suggerimenti
                if conclusion == 'failure':
                    print(f"\n🚨 === BUILD FALLITA ===")
                    print(f"💡 Per vedere l'errore:")
                    print(f"   1. Vai su: {html_url}")
                    print(f"   2. Clicca su 'Build APK' nella sezione Jobs")
                    print(f"   3. Espandi i log per trovare l'errore")
                    print(f"   4. Cerca linee che contengono 'ERROR' o 'FAILED'")
                
                # Se completata con successo
                elif conclusion == 'success':
                    print(f"\n🎉 === BUILD RIUSCITA ===")
                    print(f"✅ APK creato con successo!")
                    print(f"📱 Per scaricarlo:")
                    print(f"   1. Vai su: {html_url}")
                    print(f"   2. Scorri verso il basso alla sezione 'Artifacts'")
                    print(f"   3. Clicca su 'android-apk' per scaricare")
                    print(f"   4. Estrai lo ZIP e troverai l'APK")
                
                return status, conclusion, html_url
                
            else:
                print("❌ Nessuna build trovata")
                return None, None, None
                
        else:
            print(f"❌ Errore API GitHub: {response.status_code}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Errore nel controllo build: {e}")
        return None, None, None

def monitor_continuously():
    """Monitora le build in modo continuo"""
    print("🔄 === MONITORAGGIO CONTINUO BUILD ===")
    print("Premi Ctrl+C per fermare il monitoraggio\n")
    
    last_status = None
    last_conclusion = None
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{current_time}] Controllando build...")
            
            status, conclusion, url = check_latest_build()
            
            # Se è cambiato qualcosa, notifichiamo
            if (status, conclusion) != (last_status, last_conclusion):
                if status == 'in_progress' and last_status != 'in_progress':
                    print("🚀 === BUILD INIZIATA ===")
                elif conclusion == 'success' and last_conclusion != 'success':
                    print("🎉 === BUILD COMPLETATA CON SUCCESSO ===")
                    print("🔔 Notifica: APK pronto per il download!")
                    break  # Esce dal loop
                elif conclusion == 'failure' and last_conclusion != 'failure':
                    print("💥 === BUILD FALLITA ===")
                    print("🔔 Notifica: Controlla i log per l'errore")
                    break  # Esce dal loop
                
                last_status = status
                last_conclusion = conclusion
            
            # Se è ancora in corso, continua il monitoraggio
            if status == 'in_progress':
                print("⏳ Build ancora in corso... controllo tra 2 minuti")
                time.sleep(120)  # Aspetta 2 minuti
            elif status == 'queued':
                print("⏳ Build in coda... controllo tra 1 minuto")
                time.sleep(60)   # Aspetta 1 minuto
            else:
                break  # Build completata (successo/fallimento)
    
    except KeyboardInterrupt:
        print("\n⏹️ Monitoraggio fermato dall'utente")
    except Exception as e:
        print(f"\n❌ Errore nel monitoraggio: {e}")

def main():
    """Funzione principale"""
    print("🏛️ === MONITOR GITHUB ACTIONS BUILD APK ===\n")
    
    print("Cosa vuoi fare?")
    print("1. 📊 Controlla status build corrente")
    print("2. 🔄 Monitora build in tempo reale")
    print("3. 🔗 Apri GitHub Actions nel browser")
    
    try:
        choice = input("\nScegli opzione (1-3): ").strip()
        
        if choice == '1':
            print("\n📊 === CONTROLLO STATUS SINGOLO ===")
            check_latest_build()
            
        elif choice == '2':
            monitor_continuously()
            
        elif choice == '3':
            import webbrowser
            url = "https://github.com/digiacomovictor/MonumentRecognizer/actions"
            print(f"🌐 Aprendo: {url}")
            webbrowser.open(url)
            
        else:
            print("❌ Opzione non valida")
            
    except KeyboardInterrupt:
        print("\n👋 Uscita dall'utente")
    except Exception as e:
        print(f"\n❌ Errore: {e}")

if __name__ == "__main__":
    main()
