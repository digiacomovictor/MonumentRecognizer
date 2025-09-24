@echo off
chcp 65001 >nul
title Configuratore Google Vision API - Monument Recognizer

echo.
echo ===============================================
echo    🔧 CONFIGURATORE GOOGLE VISION API
echo        Monument Recognizer
echo ===============================================
echo.

echo 📋 Questo script ti aiuterà a configurare Google Vision API
echo    per ottenere il massimo dalle prestazioni dell'app.
echo.
echo 💡 Modalità disponibili:
echo    • OFFLINE: Funziona già (accuratezza ~65%%)
echo    • GOOGLE API: Accuratezza 90%%+ (richiede configurazione)
echo.

set /p scelta="🚀 Vuoi configurare Google Vision API? (s/n): "

if /i "%scelta%"=="n" (
    echo.
    echo 👍 Nessun problema! L'app funziona benissimo anche in modalità offline.
    echo    Puoi configurare Google Vision in qualsiasi momento eseguendo
    echo    questo file o configure_google_vision.py
    echo.
    pause
    exit /b
)

if /i "%scelta%"=="no" (
    echo.
    echo 👍 Nessun problema! L'app funziona benissimo anche in modalità offline.
    echo.
    pause
    exit /b
)

echo.
echo 🔄 Avvio configuratore interattivo...
echo.

REM Attiva l'ambiente virtuale e esegui lo script Python
call .venv\Scripts\activate.bat
python configure_google_vision.py

echo.
echo 🏁 Configurazione completata.
echo.
pause
