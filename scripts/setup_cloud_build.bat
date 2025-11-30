@echo off
chcp 65001 >nul 2>&1
cls

echo ========================================
echo   Google Cloud Build Setup
echo ========================================
echo.

REM Check if gcloud is installed
where gcloud >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: gcloud CLI not installed
    echo.
    echo Please install from: https://cloud.google.com/sdk/docs/install
    echo.
    pause
    exit /b 1
)

echo Found gcloud CLI
echo.

REM Prompt for project ID
set /p PROJECT_ID="Enter your Google Cloud Project ID: "
echo.

echo Setting up Cloud Build for project: %PROJECT_ID%
echo.

REM Enable required APIs
echo [1/5] Enabling Cloud Build API...
gcloud services enable cloudbuild.googleapis.com --project=%PROJECT_ID%

echo [2/5] Enabling Cloud Run API...
gcloud services enable run.googleapis.com --project=%PROJECT_ID%

echo [3/5] Enabling Secret Manager API...
gcloud services enable secretmanager.googleapis.com --project=%PROJECT_ID%

echo [4/5] Enabling Container Registry API...
gcloud services enable containerregistry.googleapis.com --project=%PROJECT_ID%

echo [5/5] Enabling Artifact Registry API...
gcloud services enable artifactregistry.googleapis.com --project=%PROJECT_ID%

echo.
echo ========================================
echo   APIs Enabled Successfully!
echo ========================================
echo.

echo Next Steps:
echo.
echo 1. Upload Google Sheets API JSON to Secret Manager
echo    Run: scripts\upload_secret.bat
echo.
echo 2. Connect GitHub repository to Cloud Build
echo    Visit: https://console.cloud.google.com/cloud-build/triggers
echo.
echo 3. Create a Cloud Build trigger
echo    - Source: GitHub
echo    - Repository: spica13111-netizen/newfacematch
echo    - Branch: ^main$
echo    - Configuration: Cloud Build configuration file (cloudbuild.yaml)
echo.
pause
