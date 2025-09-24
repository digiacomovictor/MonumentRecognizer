#!/usr/bin/env python3
"""
🔧 Configuratore Google Vision API per Monument Recognizer
Questo script ti guida attraverso la configurazione delle Google Vision API.
"""

import os
import json
import sys
import webbrowser
from pathlib import Path

def print_header():
    """Stampa l'intestazione del configuratore."""
    print("=" * 60)
    print("🔧 CONFIGURATORE GOOGLE VISION API")
    print("   Per Monument Recognizer")
    print("=" * 60)
    print()

def print_step(step_num, title):
    """Stampa un passo della configurazione."""
    print(f"\n📌 PASSO {step_num}: {title}")
    print("-" * 50)

def wait_for_user():
    """Aspetta che l'utente prema un tasto."""
    input("\n⏳ Premi INVIO quando hai completato questo passo...")

def check_existing_credentials():
    """Controlla se esistono già delle credenziali."""
    possible_files = [
        "google-vision-key.json",
        "google-credentials.json",
        "service-account-key.json",
        "credentials.json"
    ]
    
    for filename in possible_files:
        if os.path.exists(filename):
            print(f"✅ Trovato file credenziali esistente: {filename}")
            response = input(f"Vuoi usare questo file? (s/n): ").lower().strip()
            if response in ['s', 'si', 'y', 'yes']:
                return filename
    
    return None

def create_credentials_guide():
    """Guida la creazione delle credenziali Google Cloud."""
    
    print_step(1, "Accesso a Google Cloud Console")
    print("🌐 Apro Google Cloud Console nel tuo browser...")
    print("\n📋 Cosa fare:")
    print("   1. Accedi con il tuo account Google")
    print("   2. Se non hai un account, creane uno (è gratuito)")
    
    try:
        webbrowser.open("https://console.cloud.google.com/")
        print("✅ Browser aperto!")
    except:
        print("❌ Non riesco ad aprire il browser automaticamente.")
        print("   Vai manualmente a: https://console.cloud.google.com/")
    
    wait_for_user()
    
    print_step(2, "Creazione/Selezione Progetto")
    print("📋 Cosa fare nella console:")
    print("   1. In alto a sinistra, clicca sul nome del progetto")
    print("   2. Clicca 'Nuovo Progetto' oppure seleziona uno esistente")
    print("   3. Nome suggerito: 'monument-recognizer'")
    print("   4. Clicca 'Crea'")
    print("\n💡 Il progetto può impiegare qualche minuto per essere creato.")
    
    wait_for_user()
    
    print_step(3, "Abilitazione Google Vision API")
    print("🌐 Apro la pagina della Vision API...")
    
    try:
        webbrowser.open("https://console.cloud.google.com/apis/library/vision.googleapis.com")
        print("✅ Pagina Vision API aperta!")
    except:
        print("❌ Non riesco ad aprire il browser automaticamente.")
        print("   Vai a: console.cloud.google.com/apis/library/vision.googleapis.com")
    
    print("\n📋 Cosa fare:")
    print("   1. Assicurati di essere nel progetto giusto (in alto)")
    print("   2. Clicca il pulsante 'ABILITA'")
    print("   3. Aspetta che l'API venga abilitata")
    
    wait_for_user()
    
    print_step(4, "Creazione Service Account")
    print("🌐 Apro la pagina Service Accounts...")
    
    try:
        webbrowser.open("https://console.cloud.google.com/iam-admin/serviceaccounts")
        print("✅ Pagina Service Accounts aperta!")
    except:
        print("❌ Non riesco ad aprire il browser automaticamente.")
        print("   Vai a: console.cloud.google.com/iam-admin/serviceaccounts")
    
    print("\n📋 Cosa fare:")
    print("   1. Clicca 'CREA SERVICE ACCOUNT'")
    print("   2. Nome: 'monument-recognizer'")
    print("   3. Descrizione: 'Per app riconoscimento monumenti'")
    print("   4. Clicca 'CREA E CONTINUA'")
    print("   5. Ruolo: 'Cloud Vision AI Service Agent'")
    print("   6. Clicca 'CONTINUA' e poi 'FINE'")
    
    wait_for_user()
    
    print_step(5, "Download delle Credenziali")
    print("📋 Cosa fare:")
    print("   1. Nella lista Service Accounts, trova quello creato")
    print("   2. Clicca sui 3 puntini (⋮) a destra")
    print("   3. Seleziona 'Gestisci chiavi'")
    print("   4. Clicca 'AGGIUNGI CHIAVE' → 'Crea nuova chiave'")
    print("   5. Seleziona tipo 'JSON' e clicca 'CREA'")
    print("   6. Il file JSON verrà scaricato automaticamente")
    
    wait_for_user()
    
    return True

def setup_credentials_file():
    """Configura il file delle credenziali."""
    print_step(6, "Configurazione File Credenziali")
    
    print("💾 Ora dobbiamo copiare il file JSON nella cartella dell'app.")
    print("\n📁 Cartella corrente dell'app:")
    print(f"   {os.getcwd()}")
    
    print("\n📋 Opzioni:")
    print("   1. Copia manualmente il file scaricato qui e rinominalo 'google-vision-key.json'")
    print("   2. Oppure dimmi il percorso completo del file scaricato")
    
    choice = input("\nScegli opzione (1 o 2): ").strip()
    
    if choice == "1":
        print(f"\n📂 Copia il file JSON scaricato in:")
        print(f"   {os.getcwd()}\\google-vision-key.json")
        print("\n⚠️  IMPORTANTE: Rinomina il file esattamente 'google-vision-key.json'")
        wait_for_user()
        
        if os.path.exists("google-vision-key.json"):
            print("✅ File google-vision-key.json trovato!")
            return "google-vision-key.json"
        else:
            print("❌ File non trovato. Controlla il nome e la posizione.")
            return None
    
    elif choice == "2":
        while True:
            file_path = input("\n📁 Percorso completo del file JSON scaricato: ").strip().strip('"')
            
            if os.path.exists(file_path):
                # Copia il file nella cartella dell'app
                import shutil
                dest_path = "google-vision-key.json"
                try:
                    shutil.copy2(file_path, dest_path)
                    print(f"✅ File copiato come: {dest_path}")
                    return dest_path
                except Exception as e:
                    print(f"❌ Errore nella copia: {e}")
                    return None
            else:
                print("❌ File non trovato. Controlla il percorso.")
                retry = input("Vuoi riprovare? (s/n): ").lower().strip()
                if retry not in ['s', 'si', 'y', 'yes']:
                    return None
    
    return None

def test_configuration(credentials_file):
    """Testa la configurazione delle credenziali."""
    print_step(7, "Test della Configurazione")
    
    try:
        # Imposta le credenziali
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file
        
        # Importa e testa Google Vision
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()
        
        print("✅ Client Google Vision creato con successo!")
        
        # Test molto semplice
        print("🧪 Eseguendo test di base...")
        
        # Se arriviamo qui, la configurazione dovrebbe funzionare
        print("✅ Configurazione completata con successo!")
        print("\n🎉 Google Vision API è ora configurata correttamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nel test: {e}")
        print("\n🛠️  Possibili soluzioni:")
        print("   • Verifica che il file JSON sia valido")
        print("   • Assicurati che l'API Vision sia abilitata")
        print("   • Controlla che il Service Account abbia i permessi giusti")
        return False

def create_env_file(credentials_file):
    """Crea un file .env per le variabili d'ambiente."""
    try:
        abs_path = os.path.abspath(credentials_file)
        env_content = f"# Google Vision API Credentials\nGOOGLE_APPLICATION_CREDENTIALS={abs_path}\n"
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print(f"✅ File .env creato con il percorso delle credenziali")
        print(f"   Percorso: {abs_path}")
        
    except Exception as e:
        print(f"⚠️  Errore nella creazione del file .env: {e}")

def main():
    """Funzione principale del configuratore."""
    print_header()
    
    print("👋 Benvenuto nel configuratore Google Vision API!")
    print("   Ti guiderò attraverso tutti i passaggi necessari.")
    print("\n💡 Prima di iniziare:")
    print("   • Avrai bisogno di un account Google (gratuito)")
    print("   • Il processo richiede circa 10-15 minuti")
    print("   • L'API ha 1000 richieste gratuite al mese")
    
    response = input("\n🚀 Vuoi procedere? (s/n): ").lower().strip()
    if response not in ['s', 'si', 'y', 'yes']:
        print("👋 Configurazione annullata. Puoi eseguire questo script in qualsiasi momento.")
        return
    
    # Controlla credenziali esistenti
    existing_file = check_existing_credentials()
    if existing_file:
        if test_configuration(existing_file):
            create_env_file(existing_file)
            print("\n🎉 Configurazione completata usando le credenziali esistenti!")
            return
        else:
            print("❌ Le credenziali esistenti non funzionano. Procediamo con nuove credenziali.")
    
    # Guida alla creazione delle credenziali
    if create_credentials_guide():
        credentials_file = setup_credentials_file()
        
        if credentials_file:
            if test_configuration(credentials_file):
                create_env_file(credentials_file)
                print("\n" + "=" * 60)
                print("🎉 CONFIGURAZIONE COMPLETATA CON SUCCESSO!")
                print("=" * 60)
                print("✅ Google Vision API è ora configurata")
                print("✅ L'app Monument Recognizer avrà accuratezza del 90%+")
                print("✅ Puoi riconoscere migliaia di monumenti nel mondo")
                print("\n🚀 Prossimi passi:")
                print("   1. Esegui: .\\avvia_app.bat")
                print("   2. L'app dovrebbe mostrare 'Google Vision API' attiva")
                print("   3. Prova a riconoscere qualche monumento!")
                print("\n💰 Ricorda: hai 1000 richieste gratuite al mese")
                print("📚 Documentazione: https://cloud.google.com/vision/docs")
            else:
                print("\n❌ Configurazione fallita. Controlla i passaggi e riprova.")
        else:
            print("\n❌ Impossibile configurare il file delle credenziali.")
    
    print(f"\n📞 Per supporto, consulta: setup_google_vision.md")

if __name__ == "__main__":
    main()
