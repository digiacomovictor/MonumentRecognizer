# 🔧 Configurazione Google Vision API

Per ottenere il massimo delle prestazioni dall'app Monumento, puoi configurare Google Vision API per un riconoscimento molto più accurato dei monumenti.

## 🚀 Modalità di Funzionamento

L'app funziona in **due modalità**:

### 1. **Modalità Offline** (Predefinita)
- ✅ **Funziona sempre** senza configurazioni aggiuntive
- 📊 Accuratezza **media** (basata su analisi di forme e colori)
- 🆓 **Completamente gratuita**

### 2. **Modalità Google Vision API** (Raccomandata)
- 🎯 Accuratezza **molto alta** (riconoscimento professionale)
- 🏛️ Riconosce automaticamente **migliaia di monumenti** in tutto il mondo
- 💳 Richiede account Google Cloud (gratuito per le prime 1000 immagini/mese)

## 🔑 Come Configurare Google Vision API (Opzionale)

### Passo 1: Creare un Account Google Cloud
1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o seleziona uno esistente
3. Abilita l'API "Cloud Vision API"

### Passo 2: Creare le Credenziali
1. Vai su "IAM & Admin" > "Service Accounts"
2. Crea un nuovo Service Account
3. Scarica il file JSON delle credenziali
4. Salva il file nella cartella dell'app con nome `google-vision-key.json`

### Passo 3: Configurazione nell'App
L'app rileverà automaticamente il file delle credenziali se presente nella cartella principale.

## 📱 Come Usare l'App

### Senza Google Vision API
1. Avvia l'app con `avvia_app.bat`
2. L'app funzionerà in modalità offline
3. Seleziona le immagini e ottieni risultati di base

### Con Google Vision API
1. Metti il file `google-vision-key.json` nella cartella dell'app
2. Avvia l'app con `avvia_app.bat`
3. L'app rileverà automaticamente le API e offrirà riconoscimento avanzato

## 💰 Costi Google Vision API

- **GRATUITO** per le prime **1,000 immagini al mese**
- **$1.50** per 1,000 immagini aggiuntive
- Perfetto per uso personale e testing

## 🛠️ Risoluzione Problemi

### "Google Vision API non configurata"
- È normale se non hai configurato le API
- L'app funzionerà comunque in modalità offline

### "Credenziali non valide"
- Verifica che il file JSON sia nella cartella corretta
- Assicurati che l'API sia abilitata nel progetto Google Cloud

### "Quota superata"
- Hai superato il limite gratuito mensile
- Attendi il mese successivo o abilita la fatturazione

## 🎯 Confronto delle Modalità

| Caratteristica | Modalità Offline | Con Google Vision |
|---------------|------------------|-------------------|
| **Accuratezza** | Media (65%) | Alta (90%+) |
| **Monumenti riconosciuti** | 10 principali | Migliaia |
| **Velocità** | Veloce | Molto veloce |
| **Costo** | Gratuito | 1000 gratis/mese |
| **Configurazione** | Nessuna | 5 minuti |

---

**L'app funziona perfettamente anche senza Google Vision API!** 
La configurazione è opzionale per chi vuole il massimo delle prestazioni.

🎉 **Buon riconoscimento di monumenti!**
