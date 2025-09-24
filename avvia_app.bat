@echo off
echo ==============================================
echo             🏛️ MONUMENTO 🏛️
echo       Riconoscimento Monumenti del Mondo
echo ==============================================
echo.
echo Avviando l'applicazione...
echo.

REM Attiva l'ambiente virtuale e avvia l'app
call .venv\Scripts\activate.bat
python main.py

echo.
echo L'applicazione è stata chiusa.
pause
