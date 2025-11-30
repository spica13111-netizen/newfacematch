@echo off
chcp 65001 >nul 2>&1
cls

echo ========================================
echo   Upload Secret to Secret Manager
echo ========================================
echo.

REM Check if gcloud is installed
where gcloud >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: gcloud CLI not installed
    echo.
    pause
    exit /b 1
)

REM Prompt for project ID
set /p PROJECT_ID="Enter your Google Cloud Project ID: "
echo.

REM Check if config file exists
if not exist "config\Google Sheets API.json" (
    echo ERROR: config\Google Sheets API.json not found
    echo.
    pause
    exit /b 1
)

echo Uploading Google Sheets API credentials to Secret Manager...
echo.

REM Create secret
gcloud secrets create gcp-service-account ^
    --data-file="config\Google Sheets API.json" ^
    --project=%PROJECT_ID%

if %errorlevel% neq 0 (
    echo.
    echo Secret may already exist. Updating version...
    gcloud secrets versions add gcp-service-account ^
        --data-file="config\Google Sheets API.json" ^
        --project=%PROJECT_ID%
)

echo.
echo ========================================
echo   Secret Uploaded Successfully!
echo ========================================
echo.
echo Secret name: gcp-service-account
echo.
pause
