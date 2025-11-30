@echo off
chcp 65001 >nul
color 0C
title 웹 서버 종료

echo.
echo ╔════════════════════════════════════════════╗
echo ║          웹 서버 종료 중...                ║
echo ╚════════════════════════════════════════════╝
echo.

echo Streamlit 프로세스 종료 중...
taskkill /F /FI "WINDOWTITLE eq 📱*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Streamlit*" 2>nul

echo ngrok 프로세스 종료 중...
taskkill /F /FI "WINDOWTITLE eq 🌐*" 2>nul
taskkill /F /IM ngrok.exe 2>nul

echo Python Streamlit 프로세스 종료 중...
for /f "tokens=2" %%i in ('tasklist ^| findstr /i "python.*streamlit"') do taskkill /F /PID %%i 2>nul

echo.
echo ╔════════════════════════════════════════════╗
echo ║           종료 완료! ✅                    ║
echo ╚════════════════════════════════════════════╝
echo.
echo 모든 웹 서버가 종료되었습니다.
echo.
timeout /t 3
