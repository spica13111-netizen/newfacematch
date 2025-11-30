@echo off
echo ========================================
echo 상품 매칭 프로그램 웹 배포 시작
echo ========================================
echo.

REM 부모 디렉토리로 이동
cd /d "%~dp0.."

echo [1/2] Streamlit 실행 중...
start "Streamlit App" cmd /k "cd /d "%~dp0.." & py -m streamlit run app.py"

echo [2/2] 5초 후 ngrok 터널 생성...
timeout /t 5 /nobreak >nul

echo ngrok 실행 중...
start "ngrok Tunnel" cmd /k "cd /d "%~dp0.." & ngrok.exe http 8501"

echo.
echo ========================================
echo 배포 완료!
echo ========================================
echo.
echo 1. ngrok 창에서 URL 확인하세요
echo 2. 그 URL을 공유하면 다른 사람도 접속 가능합니다
echo.
echo 종료하려면 두 창을 모두 닫으세요.
echo.
pause
