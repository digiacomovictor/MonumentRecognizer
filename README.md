# 🏛️ Monument Recognizer v2.1

**Riconoscimento Monumenti Intelligente con GPS, Mappe, Sistema Utenti e Condivisione Social**

Un'applicazione Python avanzata per riconoscere monumenti del mondo con GPS tracking, mappe interattive, sistema utenti completo, AI-powered recognition e funzionalità social per condividere le tue scoperte.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## ✨ Funzionalità Principali

### 🏛️ Riconoscimento Monumenti
- 📷 **Riconoscimento tramite fotocamera** - Scatta foto in tempo reale
- 🖼️ **Analisi immagini esistenti** - Carica foto dalla galleria
- 🤖 **Doppia modalità AI**:
  - **Offline**: Analisi locale (~65% accuratezza)
  - **Google Vision API**: Riconoscimento professionale (90%+ accuratezza)
- 📚 **Database esteso**: Informazioni dettagliate su storia e architettura

### 🌍 GPS e Mappe Interattive
- 📍 **Localizzazione automatica** - GPS con fallback IP e Windows
- 🗺️ **Filtro per prossimità** - Monumenti vicini alla posizione
- 📊 **Tracking visite** - Cronologia completa con timestamp
- 🌐 **Mappe HTML interattive** - Visualizzazione con Folium
- 📈 **Statistiche personali** - Percorsi e analisi dei dati

### 👤 Sistema Utenti Completo
- 🔐 **Autenticazione sicura** - Hash password con salt (PBKDF2)
- 👥 **Gestione profili** - Registrazione, login e personalizzazione
- 🎫 **Sessioni persistenti** - Login automatico tra sessioni
- 📊 **Tracking personalizzato** - Visite e statistiche per utente
- 💻 **Interfacce moderne** - UI Kivy responsive e intuitive

### 🌐 Condivisione Social
- 📤 **Multi-platform sharing** - Twitter, Facebook, Instagram, WhatsApp, Telegram, LinkedIn
- 📱 **Feed interno** - Community delle scoperte nell'app
- 👍 **Interazioni social** - Like, commenti e statistiche
- 📊 **Analytics social** - Tracking condivisioni e engagement
- 🎨 **Template automatici** - Post ottimizzati per ogni piattaforma

### 🛠️ Configurazione Avanzata
- ⚡ **Setup automatico** - Installazione dipendenze one-click
- ☁️ **Google Vision setup** - Configurazione guidata API
- 💾 **Database SQLite** - Persistenza dati locale
- 📝 **Sistema logging** - Debug e monitoraggio avanzato

---

## 🚀 Installazione e Avvio

### Metodo Rapido (Raccomandato)
```batch
# Clone del progetto
git clone <repository-url>
cd MonumentRecognizer

# Avvio applicazione principale
avvia_app.bat

# Oppure demo sistema autenticazione
avvia_demo_auth.bat
```

### Setup Google Vision API (Opzionale)
```batch
# Configurazione automatica Google Vision
configura_google_vision.bat

# Oppure script Python
python configure_google_vision.py
```

---

## 📱 Come Usare

### App Principale
1. 🚀 **Avvio**: Doppio click su `avvia_app.bat`
2. 👤 **Login**: Registrati o accedi (primo avvio)
3. 📷 **Scatta/Carica**: Ottieni immagine del monumento
4. 🔍 **Riconosci**: Analizza con AI
5. 📍 **Posizione**: GPS automatico per tracking
6. 📤 **Condividi**: Pubblica sui social o nel feed interno
7. 🗺️ **Mappa**: Visualizza visite e percorsi
8. 👥 **Social**: Esplora il feed della community

### Demo Autenticazione
1. 🚀 **Avvio**: `avvia_demo_auth.bat`
2. 📝 **Registrazione**: Crea nuovo account
3. 🔑 **Login**: Accedi con credenziali
4. 👤 **Profilo**: Gestisci informazioni personali

---

## 🧪 Test del Sistema

```batch
# Test completo GPS e mapping
python test_gps_mapping.py

# Test sistema autenticazione
python test_user_system.py

# Test funzionalità social
python test_social.py

# Test configurazione Google Vision
python test_google_vision.py
```

---

## 📁 Struttura Progetto

```
MonumentRecognizer/
├── 🚀 Avvio e Demo
│   ├── avvia_app.bat              # Launcher app principale
│   ├── avvia_demo_auth.bat        # Demo autenticazione
│   └── configura_google_vision.bat # Setup Google Vision
│
├── 💻 App Principale
│   ├── main.py                    # Interfaccia utente Kivy
│   ├── monument_recognizer.py     # Engine riconoscimento AI
│   └── camera_interface.py       # Gestione fotocamera
│
├── 👤 Sistema Utenti
│   ├── user_system.py            # Backend autenticazione
│   ├── auth_ui.py                # UI login/registrazione/profilo
│   └── demo_auth.py              # App demo completa
│
├── 🌍 GPS e Mappe
│   ├── gps_manager.py            # Gestione GPS multi-platform
│   ├── visit_tracker.py          # Tracking visite
│   └── map_generator.py          # Generazione mappe Folium
│
├── 🌐 Condivisione Social
│   ├── social_sharing.py         # Engine condivisione social
│   ├── social_ui.py              # UI feed e condivisione
│   └── test_social.py            # Test funzionalità social
│
├── 🧪 Test e Configurazione
│   ├── test_user_system.py       # Test autenticazione
│   ├── test_gps_mapping.py       # Test GPS/mappe
│   ├── configure_google_vision.py # Setup automatico API
│   └── test_google_vision.py     # Verifica configurazione
│
├── 📊 Database e Configurazione
│   ├── monuments_db.json         # Database monumenti
│   ├── requirements.txt          # Dipendenze Python
│   └── setup_google_vision.md    # Guida dettagliata API
│
└── 📚 Documentazione
    ├── README.md                  # Questo file
    ├── SOCIAL_FEATURES.md         # Guida funzionalità social
    └── setup_camera_permissions.md # Guida fotocamera
```

---

## 🏛️ Monumenti Supportati

### Modalità Offline (Base - 10 Monumenti)
- 🗼 Torre Eiffel (Parigi)
- 🏟️ Colosseo (Roma)
- 🏰 Torre di Pisa (Italia)
- 🕐 Big Ben (Londra)
- 🗽 Statua della Libertà (New York)
- ✝️ Cristo Redentore (Rio de Janeiro)
- 🕌 Taj Mahal (India)
- 🏔️ Machu Picchu (Perù)
- ⛪ Notre-Dame (Parigi)
- 🏗️ Sagrada Família (Barcellona)

### Modalità Google Vision API
- **🌍 Migliaia** di monumenti, landmark e siti storici mondiale
- 🔄 **Database sempre aggiornato** con riconoscimento globale Google
- 📈 **Accuratezza 90%+** per identificazioni precise

---

## 💻 Requisiti Sistema

| Componente | Requisito |
|------------|-----------|
| **OS** | Windows 10/11 |
| **Python** | 3.8+ (auto-install) |
| **RAM** | 4GB+ consigliati |
| **Spazio** | 1GB per installazione completa |
| **Internet** | Solo per Google Vision API |
| **GPS** | Opzionale (fallback IP) |
| **Fotocamera** | Opzionale per scatti |

---

## 🔧 Tecnologie

### Backend
- 🐍 **Python 3.11** - Core dell'applicazione
- 💾 **SQLite** - Database locale per utenti e visite
- 🔐 **PBKDF2** - Hash sicuro delle password
- 📊 **JSON** - Database monumenti strutturato

### UI e Interfacce
- 🎮 **Kivy** - Interfaccia grafica cross-platform
- 🗺️ **Folium** - Mappe interattive HTML
- 📱 **Responsive Design** - Ottimizzato per schermi diversi

### AI e Computer Vision
- 👁️ **OpenCV** - Computer vision offline
- ☁️ **Google Cloud Vision** - AI professionale (opzionale)
- 🖼️ **Pillow** - Elaborazione immagini avanzata
- 🔢 **NumPy** - Calcoli matematici ottimizzati

### GPS e Localizzazione
- 🌐 **Geopy** - Geocoding e reverse geocoding
- 📍 **Windows Location API** - GPS nativo Windows
- 🌍 **IP Geolocation** - Fallback per localizzazione
- ⚡ **Multi-source GPS** - Aggregazione dati posizione

---

## 💰 Costi e Pricing

| Servizio | Costo | Limite | Note |
|----------|--------|--------|------|
| **App Core** | 🆓 Gratuita | Illimitato | Sempre free |
| **Modalità Offline** | 🆓 Gratuita | 10 monumenti | Nessun costo |
| **Google Vision API** | 🆓 1000/mese | Poi $1.50/1000 | Perfetto uso personale |
| **GPS e Mappe** | 🆓 Gratuita | Illimitato | Completamente free |
| **Sistema Utenti** | 🆓 Gratuita | Illimitato | Database locale |

---

## 🛠️ Risoluzione Problemi

### Problemi Comuni

#### "Google Vision API non configurata"
✅ **Normale!** L'app funziona in modalità offline  
🚀 **Per migliorare**: Esegui `configura_google_vision.bat`

#### GPS non funziona
📍 **Fallback attivo**: L'app usa IP geolocation automaticamente  
🔧 **Windows**: Controlla permessi localizzazione nelle impostazioni

#### Errori di login/registrazione
👤 **Password debole**: Usa almeno 8 caratteri, maiuscole, numeri, simboli  
🔐 **Account esistente**: Username e email devono essere unici

#### Problemi fotocamera
📖 **Guida dettagliata**: Consulta `setup_camera_permissions.md`  
🔄 **Riavvio**: Chiudi e riapri l'applicazione

### Debug Avanzato
```batch
# Log dettagliati
python main.py --debug

# Test componenti singoli
python test_user_system.py
python test_gps_mapping.py
python test_google_vision.py

# Reset completo
del *.db
del google-vision-key.json
avvia_app.bat
```

---

## 🌟 Caratteristiche Avanzate

### Sicurezza
- 🔐 **Hash PBKDF2** con 100.000 iterazioni
- 🧂 **Salt univoco** per ogni password
- 🎫 **Sessioni crittografate** con token sicuri
- 📊 **Log tentativi** per monitoraggio accessi

### Performance
- ⚡ **Cache intelligente** per monumenti visitati
- 🔄 **Lazy loading** per UI responsive
- 💾 **Database ottimizzato** con indici
- 🌐 **Connessioni pooled** per API calls

### Usabilità
- 📱 **Design mobile-first** per tutti i dispositivi
- 🎨 **Temi personalizzabili** per l'interfaccia
- 🔤 **Validazione input** in tempo reale
- 📊 **Statistiche visive** con grafici e mappe

---

## 📞 Supporto e Documentazione

- 📚 **Setup completo**: [setup_google_vision.md](setup_google_vision.md)
- 📷 **Fotocamera**: [setup_camera_permissions.md](setup_camera_permissions.md)
- 🧪 **Test sistema**: `python test_*.py`
- 🔧 **Configurazione**: Script `.bat` automatici
- 💬 **Issues**: GitHub repository per bug report

---

## 🔮 Prossimi Sviluppi

### In Programma
- ☁️ **Backup cloud** - Sincronizzazione dati utente
- 👥 **Multi-utente** - Condivisione visite e classifiche
- 📲 **App mobile** - Build Android/iOS native
- 🔊 **Riconoscimento vocale** - Controlli a voce
- 🌐 **Modalità offline avanzata** - Machine learning locale

### Community Features
- 🏆 **Leaderboard** - Classifiche utenti globali
- 📸 **Galleria condivisa** - Upload foto monumenti
- ⭐ **Sistema rating** - Valutazioni e recensioni
- 🎯 **Sfide** - Obiettivi e achievement

---

**🎉 Buon viaggio alla scoperta dei monumenti del mondo!**

*Sviluppato con ❤️ per esploratori, viaggiatori e amanti della storia*

---

![Footer](https://img.shields.io/badge/Made%20with-Python%20%2B%20❤️-red)
![AI](https://img.shields.io/badge/Powered%20by-AI%20%2B%20Computer%20Vision-orange)
![GPS](https://img.shields.io/badge/GPS-Enabled-green)
