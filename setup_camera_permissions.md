# Configurazione Permessi Fotocamera 📷

Questa guida spiega come configurare i permessi per la fotocamera quando si compila l'app MonumentRecognizer per dispositivi mobili.

## 📱 Android

### 1. Configurazione buildozer.spec

Se usi **Buildozer** per compilare l'app Android, aggiungi nel file `buildozer.spec`:

```ini
[app]
# ...altre configurazioni...

# Permessi richiesti
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Provider per salvare le foto
android.add_src = ./android_src

# Gradle dependencies (se necessarie)
android.gradle_dependencies = androidx.core:core:1.8.0

[buildozer]
# ...resto della configurazione...
```

### 2. File AndroidManifest.xml (se personalizzato)

Se hai un `AndroidManifest.xml` personalizzato, aggiungi:

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />

<uses-feature 
    android:name="android.hardware.camera" 
    android:required="true" />
<uses-feature 
    android:name="android.hardware.camera.autofocus" 
    android:required="false" />
```

### 3. FileProvider (per Android 7+)

Crea la cartella `android_src` e aggiungi `fileprovider.xml`:

```bash
mkdir -p android_src/res/xml
```

**android_src/res/xml/fileprovider.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<paths>
    <external-path name="external_files" path="." />
    <cache-path name="cache" path="." />
</paths>
```

### 4. Testare su Android

1. Compila l'app: `buildozer android debug`
2. Installa: `buildozer android deploy`
3. Al primo avvio, Android chiederà i permessi fotocamera
4. Accetta i permessi per utilizzare la funzionalità

## 🍎 iOS

### 1. Configurazione kivy-ios

Se usi **kivy-ios** per compilare su iOS, configura nel file `main-ios.py` o simile:

```python
# Info.plist keys da aggiungere
plist_info = {
    'NSCameraUsageDescription': 'Questa app usa la fotocamera per riconoscere monumenti scattando foto.',
    'NSPhotoLibraryUsageDescription': 'Questa app accede alle foto per analizzare immagini di monumenti.',
    'NSPhotoLibraryAddUsageDescription': 'Questa app salva le foto scattate nella libreria fotografica.',
}
```

### 2. Info.plist

Nel file `Info.plist` dell'app iOS, aggiungi:

```xml
<key>NSCameraUsageDescription</key>
<string>MonumentRecognizer usa la fotocamera per scattare foto di monumenti e riconoscerli automaticamente.</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>MonumentRecognizer accede alla libreria fotografica per selezionare immagini di monumenti da analizzare.</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>MonumentRecognizer può salvare le foto scattate nella tua libreria fotografica.</string>
```

### 3. Testare su iOS

1. Compila l'app con kivy-ios
2. Al primo utilizzo della fotocamera, iOS mostrerà un popup di richiesta permessi
3. Accetta per abilitare la funzionalità

## 💻 Desktop (Test/Sviluppo)

Su desktop, l'app proverà ad usare la webcam per simulare la fotocamera mobile:

- **Windows**: Richiede webcam configurata
- **macOS**: Può richiedere permessi fotocamera nelle impostazioni di sistema  
- **Linux**: Assicurati che `/dev/video0` sia accessibile

## 🔧 Risoluzione Problemi

### Android
```bash
# Verifica permessi dell'app installata
adb shell dumpsys package it.tuodominio.monumentrecognizer | grep permission

# Rimuovi e reinstalla se i permessi sono bloccati
adb uninstall it.tuodominio.monumentrecognizer
buildozer android debug deploy
```

### iOS
- Verifica in Impostazioni > Privacy > Fotocamera che l'app sia abilitata
- Se i permessi sono negati, disinstalla e reinstalla l'app

### Errori Comuni

**"Camera not available"**
- Verifica che il dispositivo abbia una fotocamera
- Controlla che i permessi siano stati concessi
- Su Android, prova a riavviare l'app

**"Plyer not found"**
- Installa le dipendenze: `pip install -r requirements.txt`
- Ricompila l'app includendo plyer

**"Unable to save photo"**
- Verifica permessi di scrittura (Android: WRITE_EXTERNAL_STORAGE)
- Controlla spazio disponibile sul dispositivo

## 📦 Build Commands

### Android con Buildozer
```bash
# Prima build completa
buildozer android debug

# Deploy e run su dispositivo
buildozer android debug deploy run

# Release firmata
buildozer android release
```

### iOS con kivy-ios
```bash
# Prepara l'ambiente
kivy-ios build python3 kivy

# Build dell'app
kivy-ios create MonumentRecognizer ~/MonumentRecognizer
cd MonumentRecognizer-ios
open MonumentRecognizer.xcodeproj
```

---

**Nota**: La funzionalità fotocamera richiede un dispositivo fisico per i test. Gli emulatori potrebbero non supportare completamente l'accesso alla fotocamera.
