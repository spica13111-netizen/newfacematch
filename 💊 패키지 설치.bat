@echo off
chcp 65001 >nul
color 0B
title 패키지 설치 중...

echo.
echo ╔════════════════════════════════════════════╗
echo ║     프로그램 설치 중... 잠시만 기다려주세요     ║
echo ╚════════════════════════════════════════════╝
echo.
echo 처음 실행할 때 한 번만 하면 됩니다!
echo.

REM Python check
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :python_found
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)

REM Fallback check for standard install location
set FALLBACK_PYTHON=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe
if exist "%FALLBACK_PYTHON%" (
    set PYTHON_CMD="%FALLBACK_PYTHON%"
    goto :python_found
)

echo ERROR: Python not found
echo.
pause
exit /b 1

:python_found
echo Found Python: %PYTHON_CMD%
echo.

%PYTHON_CMD% -m pip install -r requirements.txt

echo.
echo ╔════════════════════════════════════════════╗
echo ║              설치 완료! ✅                 ║
echo ╚════════════════════════════════════════════╝
echo.
echo 이제 프로그램을 사용할 수 있습니다!
echo.
echo 다음 중 하나를 실행하세요:
echo  • 💻 로컬 실행.bat (추천)
echo  • 🌐 웹으로 시작.bat
echo.
pause
