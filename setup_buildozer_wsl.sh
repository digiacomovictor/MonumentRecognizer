#!/bin/bash
# Script per installare Buildozer e dipendenze in WSL/Linux

echo "🔧 Installazione Buildozer per MonumentRecognizer"
echo "================================================="

# Aggiorna sistema
echo "📦 Aggiornamento sistema..."
sudo apt update && sudo apt upgrade -y

# Installa dipendenze di sistema  
echo "⚙️ Installazione dipendenze sistema..."
sudo apt install -y \
    python3 python3-pip python3-venv \
    git zip unzip \
    openjdk-8-jdk \
    build-essential \
    libssl-dev libffi-dev \
    libsqlite3-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libncursesw5-dev \
    xz-utils tk-dev \
    libxml2-dev libxslt1-dev \
    libjpeg-dev libpng-dev \
    autoconf libtool pkg-config

# Installa Android SDK
echo "📱 Installazione Android SDK..."
mkdir -p ~/.buildozer/android
cd ~/.buildozer/android

# Download Android SDK Command Line Tools  
if [ ! -f "cmdline-tools/latest/bin/sdkmanager" ]; then
    echo "📥 Download Android Command Line Tools..."
    wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
    unzip -q commandlinetools-linux-9477386_latest.zip
    mkdir -p cmdline-tools/latest
    mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
    rm commandlinetools-linux-9477386_latest.zip
fi

# Configura environment variables
echo "🔧 Configurazione environment..."
export ANDROID_HOME=~/.buildozer/android
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Accetta licenze Android
echo "📋 Accettazione licenze Android..."
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses || true

# Installa Android SDK packages
echo "📦 Installazione Android SDK packages..."
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager \
    "platform-tools" \
    "platforms;android-30" \
    "build-tools;30.0.3" \
    "ndk;21.4.7075529"

# Torna alla directory del progetto
cd ~/MonumentRecognizer

# Crea virtual environment
echo "🐍 Creazione virtual environment..."
python3 -m venv buildozer_env
source buildozer_env/bin/activate

# Aggiorna pip
pip install --upgrade pip setuptools wheel

# Installa Buildozer e Kivy
echo "📱 Installazione Buildozer e Kivy..."
pip install buildozer
pip install kivy kivymd
pip install cython==0.29.33

# Installa dipendenze del progetto
echo "📚 Installazione dipendenze progetto..."
pip install pillow requests folium matplotlib plotly pandas

# Installa p4a (python-for-android)
pip install python-for-android

echo ""
echo "✅ INSTALLAZIONE COMPLETATA!"
echo ""
echo "🎯 PROSSIMI PASSI:"
echo "1. Esegui: source buildozer_env/bin/activate"
echo "2. Esegui: buildozer init"  
echo "3. Modifica buildozer.spec se necessario"
echo "4. Esegui: buildozer android debug"
echo ""
echo "📱 L'APK verrà generato in bin/monumentrecognizer-0.1-arm64-v8a-debug.apk"
echo ""
