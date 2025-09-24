# 🚀 Guida: Caricare MonumentRecognizer su GitHub

## 📋 **Step 1: Installare Git**

### Metodo 1: Download Manuale (Consigliato)
1. Vai su: https://git-scm.com/download/win
2. Scarica "64-bit Git for Windows Setup"
3. Esegui installer con impostazioni predefinite
4. Riavvia PowerShell dopo installazione

### Metodo 2: Con Winget (se disponibile)
```powershell
winget install Git.Git
```

### Metodo 3: Con Chocolatey (se installato)
```powershell
choco install git
```

---

## 🌐 **Step 2: Creare Account GitHub**

Se non hai ancora un account GitHub:

1. Vai su: https://github.com
2. Clicca **"Sign up"**
3. Scegli username, email, password
4. Verifica email
5. Scegli piano gratuito

---

## 📁 **Step 3: Creare Repository GitHub**

### Via Web (Più Facile)
1. Accedi a GitHub
2. Clicca **"+"** in alto a destra → **"New repository"**
3. **Repository name**: `MonumentRecognizer`
4. **Description**: `🏛️ AI-powered monument recognition app with GPS, maps, and user dashboard`
5. **Visibility**: Public o Private (tua scelta)
6. ✅ **Add a README file**
7. ✅ **Add .gitignore** → Template: Python
8. ✅ **Choose a license** → MIT License (consigliato)
9. Clicca **"Create repository"**

### Via GitHub CLI (Alternativo)
```powershell
# Installa GitHub CLI prima
winget install GitHub.CLI

# Crea repo
gh repo create MonumentRecognizer --public --description "🏛️ AI-powered monument recognition app"
```

---

## 🔧 **Step 4: Configurare Git (Prima Volta)**

Apri PowerShell nella directory del progetto e configura Git:

```powershell
# Configura nome e email (sostituisci con i tuoi dati)
git config --global user.name "Il Tuo Nome"
git config --global user.email "tua.email@example.com"

# Verifica configurazione
git config --global --list
```

---

## 📤 **Step 5: Caricare Progetto**

### Nella directory MonumentRecognizer:

```powershell
# 1. Inizializza repository Git
git init

# 2. Aggiungi remote (sostituisci USERNAME con tuo username GitHub)
git remote add origin https://github.com/USERNAME/MonumentRecognizer.git

# 3. Aggiungi tutti i file
git add .

# 4. Controlla cosa verrà committato
git status

# 5. Crea primo commit
git commit -m "🏛️ Initial commit: Complete Monument Recognizer app with AI recognition, maps, and dashboard"

# 6. Imposta branch principale
git branch -M main

# 7. Carica su GitHub
git push -u origin main
```

---

## 🔐 **Step 6: Autenticazione GitHub**

### Prima volta che fai push, ti chiederà credenziali:

#### Opzione 1: Personal Access Token (Raccomandato)
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Scadenza: 90 days o No expiration
4. Scope: ✅ repo, ✅ workflow
5. Copia il token generato
6. **Usa il token come password** quando Git lo chiede

#### Opzione 2: GitHub Desktop (GUI)
1. Scarica: https://desktop.github.com/
2. Installa e accedi con account GitHub
3. Clone del repository o aggiungi repository esistente

---

## 📝 **Step 7: Creare .gitignore per Python**

Prima del commit, crea un file per escludere file temporanei:

```powershell
# Crea .gitignore (se non esiste)
New-Item -ItemType File -Name ".gitignore" -Force
```

Contenuto del .gitignore:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
buildozer_env/

# Buildozer
.buildozer/
bin/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# App specific
session.txt
users_db.json
monument_visits_*.json
visit_photos_*/
generated_maps/
dashboard_charts/

# Logs
*.log
```

---

## 🎯 **Step 8: Verificare Upload**

Dopo il push:

1. Vai su `https://github.com/USERNAME/MonumentRecognizer`
2. Dovresti vedere tutti i file del progetto
3. GitHub Actions dovrebbe attivarsi automaticamente per build APK

---

## 🔄 **Comandi Git Utili per il Futuro**

```powershell
# Stato repository
git status

# Aggiungere modifiche
git add .
git commit -m "Descrizione modifiche"
git push

# Vedere cronologia
git log --oneline

# Creare nuovo branch
git checkout -b feature/nuova-funzionalita

# Tornare al main
git checkout main

# Aggiornare da GitHub
git pull
```

---

## 🚀 **Step 9: Attivare GitHub Actions (APK Build)**

Una volta caricato il progetto:

1. Vai su repository GitHub
2. Tab **"Actions"**
3. Se vedi "Build Android APK" → Clicca **"Enable"**
4. Il workflow partirà automaticamente e creerà l'APK!

### Download APK da Actions:
1. Actions → Ultima build completata
2. Scroll down → **Artifacts**
3. Scarica `monument-recognizer-apk`

---

## 🔧 **Risoluzione Problemi**

### Errore: "Repository not found"
- Controlla username nel URL remote
- Verifica che repository esista su GitHub

### Errore: "Authentication failed"
- Usa Personal Access Token invece della password
- O installa GitHub Desktop per GUI

### File troppo grandi
```powershell
# Se hai file > 100MB
git lfs track "*.apk"
git add .gitattributes
```

### Resetta se necessario
```powershell
# Solo in caso di errori gravi
rm -rf .git
git init
# Ricomincia dal punto 5
```

---

## 📱 **Bonus: Build APK Automatico**

Una volta su GitHub, ogni volta che fai push:

1. GitHub Actions parte automaticamente
2. Compila APK per Android
3. APK disponibile in Releases (se main branch)
4. O in Artifacts (per test)

---

## 🎉 **Risultato Finale**

Avrai:
- ✅ Progetto completo su GitHub
- ✅ Build APK automatico
- ✅ Versioning e backup
- ✅ Collaborazione facilitata
- ✅ Portfolio professionale

**Il tuo MonumentRecognizer sarà visibile al mondo! 🌍**

---

## 📞 **Se Hai Problemi**

1. **Git non funziona**: Riavvia PowerShell dopo installazione
2. **Push fallisce**: Verifica credenziali GitHub
3. **Actions non parte**: Controlla file `.github/workflows/build_apk.yml`
4. **File mancanti**: Verifica `.gitignore`

**Repository GitHub = Portfolio + Backup + APK Build automatico!** 🎯
