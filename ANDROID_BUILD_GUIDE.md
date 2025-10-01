# 🏗️ Guida Android Build Ottimizzata - MonumentRecognizer

## 📋 Panoramica

Questa guida descrive il nuovo sistema di build Android ottimizzato che risolve i problemi di download dell'NDK e migliora l'affidabilità delle build automatiche.

## 🔧 Miglioramenti Implementati

### ✅ Problemi Risolti
- **Download NDK Fallimenti**: Utilizza NDK pre-installato da GitHub Actions
- **Timeout durante setup**: Aumentato timeout e implementato retry logic
- **Cache inefficiente**: Sistema di cache stratificato ottimizzato
- **Versioni incompatibili**: Java 17, Python 3.9, NDK 21.4.7075529
- **Monitoraggio limitato**: Script avanzati per monitoring e analisi

### 🆕 Nuove Funzionalità
- **NDK Pre-installato**: Evita download da 1GB+ durante build
- **Cache Stratificato**: Cache separato per dipendenze Python, Buildozer globale e locale
- **Retry Automatico**: 3 tentativi con pulizia cache intelligente
- **Monitoring Avanzato**: Script Python per monitoraggio real-time
- **Analisi Trend**: Statistiche su successo/fallimento delle build

## 📁 File Creati

### 1. `.github/workflows/android-build-fixed.yml`
**Nuovo workflow principale ottimizzato**
- Utilizza `android-actions/setup-android@v3` per NDK pre-installato
- Cache stratificato su 3 livelli
- Retry logic con timeout di 20 minuti per tentativo
- Upload automatico di APK e log di build

### 2. `monitor_android_build.py`
**Script di monitoraggio avanzato**
```bash
# Monitoraggio singolo
python monitor_android_build.py --owner USERNAME --repo MonumentRecognizer

# Monitoraggio continuo
python monitor_android_build.py --owner USERNAME --repo MonumentRecognizer --watch

# Analisi trend
python monitor_android_build.py --owner USERNAME --repo MonumentRecognizer --analyze
```

### 3. `test_android_build.py`
**Script per test automatico del workflow**
```bash
python test_android_build.py
```

## 🚀 Come Utilizzare

### Opzione 1: Esecuzione Manuale (Raccomandato)
1. **Vai su GitHub** → Repository → Tab "Actions"
2. **Seleziona** "Android Build - NDK Fixed"
3. **Clicca** "Run workflow" → "Run workflow"
4. **Monitora** con: `python monitor_android_build.py --owner USERNAME --repo MonumentRecognizer --watch`

### Opzione 2: Trigger Automatico
```bash
# Esegui il test suite
python test_android_build.py
```

### Opzione 3: Push/PR Automatico
Il workflow si avvia automaticamente su:
- Push su `main`/`master`
- Pull Request verso `main`/`master`

## 📊 Configurazioni Ottimali

### Workflow Settings
```yaml
timeout-minutes: 60          # Timeout per job
ndk-version: 21.4.7075529    # NDK compatibile
java-version: '17'           # Java LTS
python-version: '3.9'       # Python compatibile con Buildozer
```

### Cache Strategy
```yaml
Python deps:    ~/.cache/pip
Buildozer glob: ~/.buildozer  
Buildozer loc:  .buildozer
```

### Retry Logic
- **3 tentativi** per build completa
- **20 minuti timeout** per tentativo
- **Pulizia cache selettiva** tra tentativi
- **10 secondi pausa** tra retry

## 🔍 Monitoraggio

### Monitor Script Features
- **Status Real-time**: Stato corrente di tutti i workflow Android
- **Progress Tracking**: Step corrente per build in corso
- **Duration Tracking**: Tempo trascorso e durata media
- **Trend Analysis**: Statistiche di successo/fallimento
- **Multiple Workflows**: Supporta più workflow Android

### Comandi Utili
```bash
# Monitor basic
python monitor_android_build.py --owner USERNAME --repo REPO

# Monitor continuo ogni 30s
python monitor_android_build.py --owner USERNAME --repo REPO --watch

# Monitor continuo ogni 10s
python monitor_android_build.py --owner USERNAME --repo REPO --watch --interval 10

# Analisi trend (ultimi 20 run)
python monitor_android_build.py --owner USERNAME --repo REPO --analyze

# Con token GitHub (evita rate limiting)
python monitor_android_build.py --owner USERNAME --repo REPO --token ghp_xxxx --watch
```

## 🐛 Troubleshooting

### Build Fallisce Ancora?

1. **Controlla i log**:
   ```bash
   # Scarica log da GitHub Actions
   # oppure usa monitor script
   python monitor_android_build.py --owner USERNAME --repo REPO
   ```

2. **Verifica dipendenze Python**:
   - Controlla `requirements.txt`
   - Verifica compatibilità librerie con Android

3. **Problemi NDK**:
   - Il workflow ora usa NDK pre-installato
   - Se fallisce, può essere problema di versione in `buildozer.spec`

4. **Cache corrotto**:
   - Il workflow pulisce cache automaticamente tra retry
   - Per pulizia manuale: cancella workflow runs precedenti

### Errori Comuni

#### "NDK not found"
❌ **Problema**: Buildozer.spec ha path NDK errato
✅ **Soluzione**: Il workflow corregge automaticamente il path

#### "Timeout during build"
❌ **Problema**: Build troppo lunga (>60min)  
✅ **Soluzione**: Workflow ha timeout 60min con 3 retry (max 3h)

#### "Memory/Space issues"
❌ **Problema**: Runner GitHub ha limitazioni  
✅ **Soluzione**: Ottimizzato per GitHub runners standard

## 📈 Performance Expectations

### Tempi Medi (stimati)
- **Setup (pre-build)**: 3-5 minuti
- **Buildozer init**: 10-15 minuti  
- **Android compilation**: 15-25 minuti
- **APK packaging**: 2-5 minuti
- **Totale tipico**: 30-50 minuti

### Success Rate Target
- **Pre-ottimizzazione**: ~20-30% successo
- **Post-ottimizzazione**: ~80-90% successo target

## 🔧 Personalizzazione

### Modifica Timeout
Edita `.github/workflows/android-build-fixed.yml`:
```yaml
timeout-minutes: 90  # Aumenta se necessario
```

### Modifica Retry
Edita la sezione retry nel workflow:
```bash
for attempt in 1 2 3 4; do  # Aumenta tentativi
```

### Modifica Cache
Aggiungi cache personalizzate:
```yaml
- name: Cache Custom
  uses: actions/cache@v3
  with:
    path: ~/.custom
    key: custom-${{ hashFiles('custom.txt') }}
```

## 📞 Support

### Log Analysis
I build log sono automaticamente uploadati come artifacts in GitHub Actions.

### Monitor Advanced
Usa il monitor script per diagnosi real-time:
```bash
python monitor_android_build.py --owner USERNAME --repo REPO --watch --interval 15
```

### Debug Mode
Per debug approfondito, modifica workflow aggiungendo:
```yaml
env:
  BUILDOZER_LOG_LEVEL: 2
```

---

## 🎯 Prossimi Passi

1. **Esegui il nuovo workflow** usando una delle opzioni sopra
2. **Monitora l'esecuzione** con il monitor script  
3. **Analizza i risultati** e fornisci feedback
4. **Se fallisce**, condividi i log per ulteriori ottimizzazioni

Il nuovo sistema dovrebbe risolvere il problema del download NDK e migliorare significativamente l'affidabilità delle build Android! 🚀
