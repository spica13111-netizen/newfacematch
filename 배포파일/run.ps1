# Google Order Data Web UI - PowerShell Launch Script
# PowerShell 스크립트로 Streamlit 앱을 실행합니다.

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Google Order Data Web UI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Python 확인
Write-Host "[*] Checking Python..." -ForegroundColor Yellow

$pythonCmd = $null

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
    Write-Host "[*] Python command: python" -ForegroundColor Green
} 
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
    Write-Host "[*] Python command: py" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Python 버전 확인
Write-Host ""
Write-Host "[*] Python version:" -ForegroundColor Yellow
& $pythonCmd --version
Write-Host ""

# 현재 디렉토리 확인
Write-Host "[*] Current directory: $PWD" -ForegroundColor Yellow
Write-Host ""

# app.py 파일 존재 확인
if (-not (Test-Path "app.py")) {
    Write-Host "[ERROR] app.py file not found" -ForegroundColor Red
    Write-Host "Current directory: $PWD" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python files in this directory:" -ForegroundColor Yellow
    Get-ChildItem -Filter "*.py" | ForEach-Object { Write-Host "  - $($_.Name)" }
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[*] app.py found" -ForegroundColor Green
Write-Host ""

# Streamlit 설치 확인
Write-Host "[*] Checking Streamlit..." -ForegroundColor Yellow
$streamlitCheck = & $pythonCmd -c "import streamlit; print(f'Streamlit version: {streamlit.__version__}')" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Streamlit not installed" -ForegroundColor Yellow
    Write-Host "[*] Installing required packages..." -ForegroundColor Yellow
    Write-Host ""
    
    & $pythonCmd -m pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Package installation failed" -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
} 
else {
    Write-Host "[*] $streamlitCheck" -ForegroundColor Green
}
Write-Host ""

Write-Host "[*] Starting Web UI..." -ForegroundColor Green
Write-Host "[*] Browser will open automatically" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to exit" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Streamlit 실행
& $pythonCmd -m streamlit run app.py

# 종료 처리
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Streamlit execution failed" -ForegroundColor Red
    Write-Host "Error code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Write-Host "Program terminated." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
