#!/bin/bash

# Cloud Shell에서 실행하는 배포 스크립트

set -e  # 오류 발생 시 스크립트 중단

echo "======================================"
echo "  Cloud Run 배포 스크립트"
echo "======================================"
echo ""

# 프로젝트 ID 설정
PROJECT_ID="project-3734f652-cb10-47ac-8f3"
REGION="asia-northeast3"
SERVICE_NAME="product-matcher"

echo "프로젝트 ID: $PROJECT_ID"
echo "리전: $REGION"
echo "서비스 이름: $SERVICE_NAME"
echo ""

# 1. 프로젝트 설정
echo "[1/4] 프로젝트 설정 중..."
gcloud config set project $PROJECT_ID

# 2. GitHub에서 코드 클론 (이미 클론했다면 건너뛰기)
if [ ! -d "newfacematch" ]; then
    echo "[2/4] GitHub에서 코드 클론 중..."
    git clone https://github.com/spica13111-netizen/newfacematch.git
    cd newfacematch
else
    echo "[2/4] 기존 코드 사용 (업데이트 중)..."
    cd newfacematch
    git pull origin main
fi

echo ""
echo "현재 디렉토리: $(pwd)"
echo ""

# 3. Cloud Run에 배포
echo "[3/4] Cloud Run에 배포 중..."
echo "이 과정은 5-10분 정도 걸릴 수 있습니다..."
echo ""

gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-secrets="GCP_SERVICE_ACCOUNT=gcp-service-account:latest" \
  --project $PROJECT_ID

# 4. 배포 완료
echo ""
echo "======================================"
echo "  🎉 배포 완료!"
echo "======================================"
echo ""

# URL 가져오기
URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --project $PROJECT_ID \
  --format="value(status.url)")

echo "서비스 URL: $URL"
echo ""
echo "위 URL을 브라우저에서 열어 앱을 확인하세요!"
echo ""
