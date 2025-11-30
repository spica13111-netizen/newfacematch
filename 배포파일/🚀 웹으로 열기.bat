@echo off
chcp 65001 >nul
color 0A
title Web Deploy with ngrok

echo.
echo ========================================
echo     Web Deploy Starting
echo ========================================
echo.

REM Move to parent directory
cd /d "%~dp0.."

echo [1/2] Starting Streamlit app...
start "Streamlit App" cmd /k "title Streamlit App (DO NOT CLOSE) & cd /d "%~dp0.." & py -m streamlit run app.py --server.port 8501"

echo [2/2] Waiting 5 seconds for ngrok...
timeout /t 5 /nobreak >nul

echo Starting ngrok tunnel...
start "ngrok Tunnel" cmd /k "title ngrok Tunnel - Check URL (DO NOT CLOSE) & cd /d "%~dp0.." & echo. & echo ===================================== & echo   Check ngrok tunnel URL below! & echo ===================================== & echo. & ngrok.exe http 8501"

echo.
echo ========================================
echo          Deploy Complete!
echo ========================================
echo.
echo How to use:
echo.
echo 1. Check "Forwarding" URL in ngrok window
echo    Example: https://xxxx.ngrok-free.app
echo.
echo 2. Copy and share that URL
echo.
echo 3. To stop: Close both windows
echo.
echo WARNING: Connection stops when PC is off!
echo.
pause
