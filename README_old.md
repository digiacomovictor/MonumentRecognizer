# 🏛️ Monument Recognizer

**Riconoscimento Monumenti del Mondo con Intelligenza Artificiale**

Un'applicazione Python con interfaccia grafica per riconoscere monumenti famosi in tutto il mondo utilizzando computer vision avanzata.

## 🚀 Funzionalità

- **📷 Riconoscimento tramite fotocamera**: Scatta foto in tempo reale
- **🖼️ Riconoscimento da file**: Analizza immagini esistenti
- **🤖 Doppia modalità AI**:
  - **Modalità Offline**: Analisi locale (accuratezza ~65%)
  - **Modalità Google Vision API**: Riconoscimento professionale (accuratezza 90%+)
- **📚 Database monumenti**: Informazioni dettagliate su storia, architettura e curiosità
- **💻 Interfaccia user-friendly**: Design intuitivo simile a un'app mobile

## 📦 Installazione Rapida

1. **Clona il progetto**:
   ```bash
   git clone <repository-url>
   cd MonumentRecognizer
   ```

2. **Avvia l'applicazione**:
   ```batch
   .\avvia_app.bat
   ```
   
   Il primo avvio installerà automaticamente tutte le dipendenze!

## 🔧 Configurazione Google Vision API (Opzionale)

### Perché configurare Google Vision?

| Modalità | Accuratezza | Monumenti | Costo |
|----------|-------------|-----------|-------|
| **Offline** | ~65% | 10 principali | Gratuito |
| **Google Vision** | 90%+ | Migliaia | 1000 gratis/mese |

### 🎯 Configurazione Automatica

**Opzione 1 - Script Automatico**:
```batch
.\configura_google_vision.bat
```

**Opzione 2 - Script Python**:
```bash
python configure_google_vision.py
```

### 📋 Passi Manuali (se preferisci)

1. **Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com/)
2. **Crea progetto**: `monument-recognizer`
3. **Abilita API**: Cloud Vision API
4. **Service Account**: Crea con ruolo "Cloud Vision AI Service Agent"
5. **Download JSON**: Salva come `google-vision-key.json` nella cartella dell'app

### 🧪 Test della Configurazione

```bash
python test_google_vision.py
```

## 📱 Come Usare

1. **Avvia l'app**: `avvia_app.bat`
2. **Scegli il metodo**:
   - 📷 **Scatta Foto**: Usa la fotocamera
   - 🖼️ **Scegli Immagine**: Seleziona file esistente
3. **Analizza**: Clicca "Riconosci Monumento"
4. **Scopri**: Leggi storia e dettagli del monumento!

## 🏛️ Monumenti Supportati

### Modalità Offline (Base)
- Torre Eiffel (Parigi)
- Torre di Pisa (Italia) 
- Colosseo (Roma)
- Big Ben (Londra)
- Statua della Libertà (New York)
- Cristo Redentore (Rio de Janeiro)
- Taj Mahal (India)
- Machu Picchu (Perù)
- Notre-Dame (Parigi)
- Sagrada Família (Barcellona)

### Modalità Google Vision API
- **Migliaia** di monumenti, landmark e siti storici in tutto il mondo
- Riconoscimento automatico basato su database globale Google
- Costante aggiornamento e miglioramento

## 🛠️ Risoluzione Problemi

### "Google Vision API non configurata"
✅ **Normale!** L'app funziona perfettamente in modalità offline
🚀 **Per migliorare**: Esegui `configura_google_vision.bat`

### Problemi con la fotocamera
📖 Consulta: `setup_camera_permissions.md`

### Errori generali
1. **Riavvia l'app**: Chiudi e riapri `avvia_app.bat`
2. **Controlla connessione**: Per Google Vision API
3. **Reinstalla dipendenze**: Elimina `.venv` e riavvia

## 📁 Struttura Progetto

```
MonumentRecognizer/
├── 📱 avvia_app.bat              # Avvio applicazione
├── 🔧 configura_google_vision.bat # Configurazione Google API
├── 🧪 test_google_vision.py      # Test configurazione
├── 🎯 main.py                    # App principale
├── 🤖 monument_recognizer.py     # Engine AI
├── 📷 camera_interface.py        # Gestione fotocamera
├── 📊 monuments_db.json          # Database monumenti
├── 📋 requirements.txt           # Dipendenze Python
├── 📚 setup_google_vision.md     # Guida dettagliata API
└── 🔍 setup_camera_permissions.md# Guida fotocamera
```

## 💻 Requisiti Sistema

- **OS**: Windows 10/11
- **Python**: 3.8+ (installato automaticamente se mancante)
- **RAM**: 4GB+ consigliati
- **Spazio**: 500MB per installazione completa
- **Internet**: Solo per configurazione Google Vision API
- **Fotocamera**: Opzionale, per scatto foto

## 🎨 Tecnologie

- **🐍 Python**: Core dell'applicazione
- **🎮 Kivy**: Interfaccia grafica moderna
- **👁️ OpenCV**: Computer vision offline
- **☁️ Google Cloud Vision**: AI avanzata (opzionale)
- **🖼️ Pillow**: Elaborazione immagini
- **📊 NumPy**: Calcoli matematici

## 💰 Costi

- **App**: Completamente gratuita
- **Modalità Offline**: Sempre gratuita
- **Google Vision API**: 
  - 🆓 Prime 1.000 richieste/mese gratuite
  - 💵 $1.50 per 1.000 richieste aggiuntive
  - Perfetto per uso personale!

## 📞 Supporto

- 📚 **Guida completa**: `setup_google_vision.md`
- 📷 **Problemi fotocamera**: `setup_camera_permissions.md`
- 🧪 **Test sistema**: `python test_google_vision.py`
- 🔧 **Configurazione**: `configura_google_vision.bat`

---

**🎉 Buon riconoscimento di monumenti!**

*Sviluppato con ❤️ per gli amanti della storia e dell'architettura*

# 🏛️ Monumento

Un'app mobile realizzata in Python che riconosce monumenti famosi del mondo tramite analisi delle immagini e fornisce informazioni storiche dettagliate.

## 🌟 Caratteristiche

- **📷 Fotocamera Integrata** - Scatta foto direttamente dall'app
- **🖼️ Caricamento Immagini** - Seleziona foto dalla galleria
- **🔍 Riconoscimento Automatico** - Identifica monumenti famosi istantaneamente  
- **📚 Descrizioni Storiche** - Informazioni complete di ogni monumento
- **📱 Interfaccia Mobile** - Design ottimizzato per smartphone
- **🌐 Cross-Platform** - Funziona su Android, iOS, Windows, macOS, Linux
- **🔥 Modalità Online** - Google Vision API (90%+ accuratezza)
- **💻 Modalità Offline** - Funzionamento senza internet (65% accuratezza)

## 🏛️ Monumenti Supportati

L'app può riconoscere i seguenti monumenti famosi:

- 🗼 **Torre Eiffel** (Parigi, Francia)
- 🏰 **Torre di Pisa** (Pisa, Italia)
- 🏟️ **Colosseo** (Roma, Italia)
- 🕐 **Big Ben** (Londra, Inghilterra)
- 🗽 **Statua della Libertà** (New York, USA)
- ✝️ **Cristo Redentore** (Rio de Janeiro, Brasile)
- 🕌 **Taj Mahal** (Agra, India)
- 🏔️ **Machu Picchu** (Cusco, Perù)

## 🚀 Installazione e Avvio

### Metodo Semplice (Raccomandato)
1. **Doppio clic** su `avvia_app.bat`
2. L'app si avvierà automaticamente installando tutto il necessario

### Metodo Manuale
1. Apri il terminale nella cartella del progetto
2. Esegui: `.venv\Scripts\python.exe main.py`

## 📱 Come Usare l'App

1. **Avvia l'applicazione** 
2. **Ottieni un'immagine** in uno di questi modi:
   - 📷 **Scatta Foto**: clicca "Scatta Foto" per usare la fotocamera
   - 🖼️ **Scegli Immagine**: seleziona una foto esistente dalla galleria
3. **Analizza l'immagine** cliccando su "🔍 Riconosci Monumento"
4. **Leggi la storia** del monumento riconosciuto con dettagli completi

## 💡 Suggerimenti

- Usa immagini chiare e ben illuminate
- Il monumento deve essere ben visibile
- Funziona meglio con foto frontali

## 🛠️ Struttura del Progetto

```
MonumentRecognizer/
├── main.py                       # Interfaccia utente principale
├── monument_recognizer.py        # Algoritmo di riconoscimento
├── camera_interface.py           # Gestione fotocamera mobile
├── monuments_db.json            # Database monumenti
├── requirements.txt             # Dipendenze Python
├── avvia_app.bat               # Script di avvio rapido
├── setup_camera_permissions.md  # Configurazione mobile
├── setup_google_vision.md      # Configurazione API Google
└── README.md                   # Documentazione principale
```

## 🔧 Tecnologie

- **Python 3.11** - Linguaggio principale
- **Kivy 2.2.0** - Interfaccia mobile cross-platform
- **Plyer 2.1.0** - Accesso hardware nativo (fotocamera)
- **OpenCV 4.8** - Computer vision e analisi immagini
- **Google Vision API** - Riconoscimento monumenti avanzato
- **NumPy** - Calcoli numerici e matematici
- **Pillow** - Elaborazione immagini

## 📱 Build per Mobile

Per compilare l'app per dispositivi mobili:

### Android
```bash
# Installa Buildozer
pip install buildozer

# Configura e compila
buildozer init
buildozer android debug
```

### iOS  
```bash
# Installa kivy-ios
pip install kivy-ios
kivy-ios build python3 kivy

# Crea progetto Xcode
kivy-ios create MonumentRecognizer ~/MonumentRecognizer
```

📄 **Importante**: Leggi `setup_camera_permissions.md` per configurare i permessi fotocamera.

---
**Creato con ❤️ in Python | 📷 Fotocamera integrata con Plyer**
