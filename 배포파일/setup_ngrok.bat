@echo off
REM 부모 디렉토리로 이동
cd /d "%~dp0.."

echo ngrok 인증 설정
echo.
echo 1. https://dashboard.ngrok.com/get-started/your-authtoken 접속
echo 2. Authtoken 복사
echo 3. 아래에 붙여넣기
echo.
set /p TOKEN="Authtoken 입력: "
ngrok.exe config add-authtoken %TOKEN%
echo.
echo 설정 완료! 이제 ngrok을 실행합니다...
echo.
pause
ngrok.exe http 8501
