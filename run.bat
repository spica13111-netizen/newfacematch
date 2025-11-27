@echo off
REM UTF-8 인코딩 설정 (실패해도 계속 진행)
chcp 65001 2>nul 1>nul
echo ========================================
echo Google Order Data Web UI
echo ========================================
echo.

REM Python 확인
echo [*] Checking Python...
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :python_found
)

echo [ERROR] Python not found in PATH
echo Please install Python 3.8 or higher
echo.
pause
exit /b 1

:python_found
echo [*] Python command: %PYTHON_CMD%

REM Python 버전 확인
echo [*] Python version:
%PYTHON_CMD% --version
echo.

REM 현재 디렉토리 확인
echo [*] Current directory: %CD%
echo.

REM app.py 파일 존재 확인
if not exist "app.py" (
    echo [ERROR] app.py file not found
    echo Current directory: %CD%
    echo.
    echo Python files in this directory:
    dir /b *.py
    echo.
    pause
    exit /b 1
)
echo [*] app.py found
echo.

REM Streamlit 설치 확인
echo [*] Checking Streamlit...
%PYTHON_CMD% -c "import streamlit; print(f'Streamlit version: {streamlit.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo [!] Streamlit not installed
    echo [*] Installing required packages...
    echo.
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Package installation failed
        echo.
        pause
        exit /b 1
    )
    echo.
) else (
    %PYTHON_CMD% -c "import streamlit; print(f'[*] Streamlit version: {streamlit.__version__}')"
)
echo.

echo [*] Starting Web UI...
echo [*] Browser will open automatically
echo.
echo Press Ctrl+C to exit
echo ========================================
echo.

REM Streamlit 실행
%PYTHON_CMD% -m streamlit run app.py

REM 종료 시 대기
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Streamlit execution failed
    echo Error code: %errorlevel%
    echo.
)
echo.
echo Program terminated.
pause
