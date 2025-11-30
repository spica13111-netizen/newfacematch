@echo off
chcp 65001 >nul
color 0B
title Google Cloud Run 배포

echo.
echo ╔════════════════════════════════════════════╗
echo ║     Google Cloud Run 배포 시작            ║
echo ╚════════════════════════════════════════════╝
echo.
echo 문서/CLOUD_RUN_DEPLOY.md 파일을 먼저 읽어보세요!
echo.
pause

echo.
echo [1/3] Google Cloud 로그인...
gcloud auth login

echo.
echo [2/3] 프로젝트 ID 입력
set /p PROJECT_ID="프로젝트 ID 입력: "
gcloud config set project %PROJECT_ID%

echo.
echo [3/3] Cloud Run에 배포...
echo.
echo 옵션 선택:
echo 1. 자동 배포 (소스코드에서 직접)
echo 2. Docker 이미지 빌드 후 배포
echo.
set /p CHOICE="선택 (1 or 2): "

if "%CHOICE%"=="1" (
    echo.
    echo 자동 배포 시작...
    gcloud run deploy product-matcher ^
      --source . ^
      --region asia-northeast3 ^
      --allow-unauthenticated ^
      --memory 1Gi ^
      --cpu 1 ^
      --max-instances 10
) else (
    echo.
    echo Cloud Build로 배포...
    gcloud builds submit --config cloudbuild.yaml
)

echo.
echo ╔════════════════════════════════════════════╗
echo ║              배포 완료!                    ║
echo ╚════════════════════════════════════════════╝
echo.
echo URL 확인:
gcloud run services describe product-matcher ^
  --region asia-northeast3 ^
  --format="value(status.url)"
echo.
pause
