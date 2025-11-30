@echo off
chcp 65001 >nul 2>&1
cls
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     Google Cloud 프로젝트 자동 설정                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if gcloud is installed
where gcloud >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: gcloud CLI가 설치되어 있지 않습니다
    echo.
    echo 다운로드: https://cloud.google.com/sdk/docs/install
    echo.
    pause
    exit /b 1
)

echo ✅ gcloud CLI 발견
echo.

REM 프로젝트 ID 입력
set /p PROJECT_ID="Google Cloud 프로젝트 ID 입력 (예: project-3734f652-cb10-47ac-8f3): "
echo.

REM 프로젝트 ID 확인
echo [확인] 프로젝트 ID: %PROJECT_ID%
echo.
set /p CONFIRM="이 프로젝트 ID가 맞습니까? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo 취소되었습니다.
    pause
    exit /b 0
)

echo.
echo ════════════════════════════════════════════════════════════
echo   단계 1: Google Cloud 로그인
echo ════════════════════════════════════════════════════════════
echo.

gcloud auth login
if %errorlevel% neq 0 (
    echo ❌ 로그인 실패
    pause
    exit /b 1
)

echo.
echo ✅ 로그인 성공
echo.

echo.
echo ════════════════════════════════════════════════════════════
echo   단계 2: 프로젝트 설정
echo ════════════════════════════════════════════════════════════
echo.

gcloud config set project %PROJECT_ID%
if %errorlevel% neq 0 (
    echo ❌ 프로젝트 설정 실패
    echo.
    echo 프로젝트 ID가 정확한지 확인하세요.
    pause
    exit /b 1
)

echo ✅ 프로젝트 설정 완료
echo.

echo.
echo ════════════════════════════════════════════════════════════
echo   단계 3: 필수 API 활성화
echo ════════════════════════════════════════════════════════════
echo.

echo [1/5] Cloud Build API 활성화 중...
gcloud services enable cloudbuild.googleapis.com --project=%PROJECT_ID%

echo [2/5] Cloud Run API 활성화 중...
gcloud services enable run.googleapis.com --project=%PROJECT_ID%

echo [3/5] Secret Manager API 활성화 중...
gcloud services enable secretmanager.googleapis.com --project=%PROJECT_ID%

echo [4/5] Container Registry API 활성화 중...
gcloud services enable containerregistry.googleapis.com --project=%PROJECT_ID%

echo [5/5] Artifact Registry API 활성화 중...
gcloud services enable artifactregistry.googleapis.com --project=%PROJECT_ID%

echo.
echo ✅ 모든 API 활성화 완료
echo.

echo.
echo ════════════════════════════════════════════════════════════
echo   단계 4: Google Sheets API 인증 정보 업로드
echo ════════════════════════════════════════════════════════════
echo.

REM 부모 디렉토리로 이동
cd /d "%~dp0.."

REM Check if config file exists
if not exist "config\Google Sheets API.json" (
    echo ❌ ERROR: config\Google Sheets API.json 파일을 찾을 수 없습니다
    echo.
    echo 이 파일이 필요합니다. 프로젝트 관리자에게 문의하세요.
    echo.
    pause
    exit /b 1
)

echo Google Sheets API 인증 정보를 Secret Manager에 업로드 중...
echo.

REM Create secret
gcloud secrets create gcp-service-account --data-file="config\Google Sheets API.json" --project=%PROJECT_ID% 2>nul

if %errorlevel% neq 0 (
    echo.
    echo Secret이 이미 존재합니다. 새 버전으로 업데이트 중...
    gcloud secrets versions add gcp-service-account --data-file="config\Google Sheets API.json" --project=%PROJECT_ID%
    
    if %errorlevel% neq 0 (
        echo ❌ Secret 업로드 실패
        pause
        exit /b 1
    )
)

echo.
echo ✅ Secret 업로드 완료 (Secret 이름: gcp-service-account)
echo.

echo.
echo ════════════════════════════════════════════════════════════
echo   단계 5: Cloud Build 서비스 계정 권한 설정
echo ════════════════════════════════════════════════════════════
echo.

echo 다음 페이지에서 권한을 수동으로 설정해야 합니다:
echo.
echo 🌐 https://console.cloud.google.com/cloud-build/settings/service-account?project=%PROJECT_ID%
echo.
echo 다음 권한을 "사용 설정"으로 변경하세요:
echo   ✓ Cloud Run 관리자
echo   ✓ Service Account 사용자
echo   ✓ Secret Manager 보안 비밀 접근자
echo.
echo 페이지를 여시겠습니까? (Y/N)
set /p OPEN_BROWSER="선택: "
if /i "%OPEN_BROWSER%"=="Y" (
    start https://console.cloud.google.com/cloud-build/settings/service-account?project=%PROJECT_ID%
)
echo.
echo 권한 설정을 완료한 후 계속하려면 아무 키나 누르세요...
pause >nul
echo.

echo.
echo ════════════════════════════════════════════════════════════
echo   단계 6: GitHub 저장소 연결 (선택사항)
echo ════════════════════════════════════════════════════════════
echo.

echo GitHub 자동 배포를 설정하시겠습니까?
echo (코드를 푸시하면 자동으로 Cloud Run에 배포됩니다)
echo.
set /p SETUP_GITHUB="GitHub 연결 설정? (Y/N): "

if /i "%SETUP_GITHUB%"=="Y" (
    echo.
    echo 다음 페이지에서 GitHub 저장소를 연결하세요:
    echo.
    echo 🌐 https://console.cloud.google.com/cloud-build/triggers?project=%PROJECT_ID%
    echo.
    echo 설정 방법:
    echo   1. "트리거 만들기" 클릭
    echo   2. 이름: github-auto-deploy
    echo   3. 이벤트: "브랜치에 푸시"
    echo   4. 소스: GitHub 연결 후 "spica13111-netizen/newfacematch" 선택
    echo   5. 브랜치: ^main$
    echo   6. 구성: Cloud Build 구성 파일 (cloudbuild.yaml)
    echo   7. "만들기" 클릭
    echo.
    start https://console.cloud.google.com/cloud-build/triggers?project=%PROJECT_ID%
    echo.
    echo GitHub 연결 설정을 완료한 후 계속하려면 아무 키나 누르세요...
    pause >nul
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                  🎉 설정 완료!                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 프로젝트 ID: %PROJECT_ID%
echo.
echo 📝 다음 단계:
echo.
echo   방법 1: 수동으로 Cloud Run에 배포
echo   ───────────────────────────────────────
echo   배포파일\🚀 Cloud Run 배포.bat 실행
echo.
echo   방법 2: GitHub 자동 배포 (설정한 경우)
echo   ───────────────────────────────────────
echo   git push origin main
echo   → 자동으로 배포됩니다!
echo.
echo 📖 자세한 내용은 문서\Cloud_Run_배포_가이드.md 참고
echo.
pause
