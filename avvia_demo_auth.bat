@echo off
title Monument Recognizer - Demo Autenticazione
cls

echo.
echo ================================================
echo    🏛️ MONUMENT RECOGNIZER v2.0
echo    Demo Sistema Autenticazione
echo ================================================
echo.
echo 🚀 Avvio demo interfaccia utente...
echo.

cd /d "%~dp0"

python demo_auth.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Errore nell'avvio della demo!
    echo    Controlla che Python e Kivy siano installati.
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 👋 Demo terminata.
pause
