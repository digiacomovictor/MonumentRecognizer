# 📱 Guida Completa: Creare APK Monument Recognizer

## 🎯 Panoramica

Questo documento ti guida nella conversione dell'app **Monument Recognizer** da applicazione Python/Kivy a **file APK Android**.

---

## ⚠️ Limitazioni Windows

**Buildozer NON funziona nativamente su Windows**. Hai queste opzioni:

### 🥇 **OPZIONE 1: WSL2 (Raccomandato)**

#### Step 1: Installa WSL2
```powershell
# Esegui come AMMINISTRATORE in PowerShell
wsl --install -d Ubuntu-22.04
```

#### Step 2: Riavvia e configura Ubuntu
1. Riavvia il PC
2. Apri "Ubuntu 22.04" dal menu Start  
3. Crea username e password Linux

#### Step 3: Copia progetto in WSL
```bash
# Nel terminale Ubuntu
cp -r /mnt/c/Users/digia/MonumentRecognizer ~/
cd MonumentRecognizer
```

#### Step 4: Esegui setup automatico
```bash
chmod +x setup_buildozer_wsl.sh
./setup_buildozer_wsl.sh
```

#### Step 5: Build APK
```bash
source buildozer_env/bin/activate
buildozer android debug
```

---

### 🥈 **OPZIONE 2: Docker**

#### Prerequisiti
- Docker Desktop installato su Windows

#### Build con Docker
```powershell
# Nella directory MonumentRecognizer
docker build -t monument-recognizer-builder .
docker run --rm -v ${PWD}:/app/output monument-recognizer-builder
```

---

### 🥉 **OPZIONE 3: GitHub Actions (Cloud)**

#### Setup
1. Carica progetto su GitHub
2. Abilita Actions nel repository
3. Il file `.github/workflows/build_apk.yml` è già configurato

#### Processo
- **Push automatico**: APK si genera ad ogni push
- **Manuale**: Vai su Actions → Build Android APK → Run workflow
- **Download**: Scarica APK da Artifacts o Releases

---

## 🔧 **Configurazione buildozer.spec**

Il file `buildozer.spec` è già configurato con:

### 📋 **Impostazioni Principali**
```ini
title = Monument Recognizer
package.name = monumentrecognizer
package.domain = com.monumentrecognizer
version = 1.0.0
```

### 🔐 **Permessi Android**
```ini
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WAKE_LOCK
```

### 📦 **Dipendenze**
```ini
requirements = python3,kivy,pillow,requests,matplotlib,plotly,pandas,folium,kivymd,plyer
```

---

## 🎨 **Assets Opzionali**

### Icona App (512x512 px)
```ini
# In buildozer.spec, rimuovi il # per abilitare
icon.filename = %(source.dir)s/data/icon.png
```

### Splash Screen
```ini
# In buildozer.spec, rimuovi il # per abilitare
presplash.filename = %(source.dir)s/data/presplash.png
```

---

## 🚀 **Processo Build Dettagliato**

### 1. **Preparazione Ambiente**
- ✅ Python 3.8+ installato
- ✅ Java 8 JDK installato  
- ✅ Android SDK configurato
- ✅ Dipendenze sistema installate

### 2. **Prima Build**
```bash
# Attiva environment
source buildozer_env/bin/activate

# Prima build (lunga, ~30-60 min)
buildozer android debug
```

### 3. **Build Successive**
```bash
# Build più veloci (~5-10 min)
buildozer android debug --verbose
```

### 4. **Output**
```
📁 bin/
   └── monumentrecognizer-1.0.0-arm64-v8a-debug.apk
```

---

## 🔧 **Risoluzione Problemi**

### ❌ **Errori Comuni**

#### "SDK not found"
```bash
export ANDROID_HOME=~/.buildozer/android
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
```

#### "Java version error"
```bash
sudo apt install openjdk-8-jdk
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

#### "Build failed - NDK"
```bash
# In buildozer.spec
android.ndk = 21.4.7075529
```

#### "Memory error"
```bash
# Aumenta memoria disponibile
buildozer android debug --verbose
```

### 🔍 **Debug Build**
```bash
# Log dettagliati
buildozer android debug --verbose

# Log buildozer
cat .buildozer/logs/buildozer.log

# Pulizia cache (se necessario)
buildozer android clean
```

---

## 🎯 **Ottimizzazioni**

### 📦 **APK Release (Più Piccolo)**
```bash
buildozer android release
# Genera APK firmato per Play Store
```

### 🎨 **Icone Multiple**
Crea icone di diverse dimensioni in `data/`:
- `icon-48.png` (48x48)
- `icon-72.png` (72x72)  
- `icon-96.png` (96x96)
- `icon-144.png` (144x144)
- `icon-192.png` (192x192)

### ⚡ **Build Veloce**
```bash
# Evita rebuild completo
buildozer android debug --private
```

---

## 📱 **Installazione APK**

### Su Dispositivo Android
1. **Abilita** "Origini sconosciute" in Impostazioni → Sicurezza
2. **Trasferisci** APK sul dispositivo
3. **Tocca** APK per installare
4. **Concedi** permessi quando richiesti

### Permessi Richiesti
- 📷 **Fotocamera**: Per scattare foto monumenti
- 📍 **Posizione**: Per GPS e monumenti vicini  
- 💾 **Storage**: Per salvare visite e foto
- 🌐 **Internet**: Per Google Vision API e mappe

---

## 🎉 **Testing APK**

### Test Funzionalità
1. ✅ **Launch**: App si avvia senza crash
2. ✅ **Login**: Sistema utenti funziona
3. ✅ **Camera**: Fotocamera si attiva
4. ✅ **Recognition**: Riconoscimento offline funziona
5. ✅ **GPS**: Localizzazione attiva
6. ✅ **Maps**: Mappe si aprono nel browser
7. ✅ **Dashboard**: Statistiche si generano

### Performance
- **Tempo avvio**: < 5 secondi
- **Memoria**: < 200MB RAM
- **Storage**: < 50MB installato

---

## 📊 **Dimensioni Finali**

| Componente | Dimensione |
|------------|------------|
| APK Debug | ~25-40 MB |
| APK Release | ~15-25 MB |
| Installato | ~40-60 MB |

---

## 🔗 **Link Utili**

- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Kivy Android Deployment](https://kivy.org/doc/stable/guide/packaging-android.html)
- [Python-for-Android](https://python-for-android.readthedocs.io/)

---

## 🎯 **Prossimi Passi**

1. **Scegli metodo** (WSL2 consigliato)
2. **Segui setup** per il metodo scelto
3. **Genera APK** con buildozer
4. **Testa APK** su dispositivo Android
5. **Deploy** (Play Store o distribuzione diretta)

---

**🏛️ Monument Recognizer è ora pronto per Android!** 📱✨
