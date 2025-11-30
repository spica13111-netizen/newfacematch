@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo    Local Run Mode
echo ========================================
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

REM Streamlit credentials setup
echo Setting up Streamlit...
%PYTHON_CMD% scripts/setup_streamlit.py >nul 2>&1
echo.

REM Run Streamlit
echo Starting program...
echo Browser will open automatically
echo Press Ctrl+C to stop
echo ========================================
echo.

%PYTHON_CMD% -m streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start
    echo Please install packages first
    echo.
)

pause
