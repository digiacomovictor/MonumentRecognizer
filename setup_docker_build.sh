#!/bin/bash
# Script per build APK in Docker

echo "🐳 Build APK Monument Recognizer in Docker"
echo "============================================"

# Assicura che buildozer.spec esista
if [ ! -f "buildozer.spec" ]; then
    echo "🔧 Inizializzazione buildozer..."
    buildozer init
fi

# Inizia build APK
echo "📱 Avvio build APK..."
buildozer android debug

# Controlla se APK è stato creato
if [ -f "bin/*.apk" ]; then
    echo "✅ APK creato con successo!"
    echo "📁 File disponibili in bin/"
    ls -la bin/
else
    echo "❌ Errore durante la creazione dell'APK"
    echo "🔍 Log di debug:"
    cat .buildozer/logs/buildozer.log | tail -50
fi
