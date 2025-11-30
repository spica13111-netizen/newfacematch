# Google Cloud Run 배포 가이드

## 📋 준비사항

1. Google Cloud 계정 (무료 크레딧 $300)
2. 결제 계정 설정 (무료 tier 내에서 사용 가능)
3. Google Cloud SDK 설치 (또는 Cloud Shell 사용)

---

## 🚀 배포 단계

### 1단계: Google Cloud 프로젝트 설정

#### 1-1. 프로젝트 생성
1. https://console.cloud.google.com 접속
2. 우측 상단 프로젝트 선택 → **새 프로젝트**
3. 프로젝트 이름: `product-matcher` (원하는 이름)
4. **만들기** 클릭

#### 1-2. API 활성화
좌측 메뉴 → **API 및 서비스** → **라이브러리**에서 다음 API 활성화:
- Cloud Run API
- Cloud Build API
- Artifact Registry API (또는 Container Registry API)
- Secret Manager API

---

### 2단계: Google Cloud SDK 설치

#### 방법 1: Cloud Shell 사용 (추천 - 가장 쉬움)
1. https://console.cloud.google.com 우측 상단 Cloud Shell 아이콘 클릭
2. 브라우저에서 터미널이 열립니다
3. SDK 설치 불필요! 바로 사용 가능

#### 방법 2: 로컬에 설치
1. https://cloud.google.com/sdk/docs/install 에서 다운로드
2. 설치 후 PowerShell에서:
```powershell
gcloud init
gcloud auth login
```

---

### 3단계: Secrets 설정 (Google Sheets API 키)

#### Secret Manager에 서비스 계정 키 저장

**Cloud Shell 또는 로컬 터미널에서:**

```bash
# 프로젝트 ID 설정 (본인의 프로젝트 ID로 변경)
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Secret 생성 (config/Google Sheets API.json 파일 내용을 Secret으로 저장)
gcloud secrets create gcp-service-account \
  --data-file=config/Google\ Sheets\ API.json \
  --replication-policy="automatic"

# Cloud Run에서 Secret 접근 권한 부여
gcloud secrets add-iam-policy-binding gcp-service-account \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

### 4단계: Docker 이미지 빌드 및 배포

#### 방법 1: 자동 배포 (Cloud Build 사용)

**GitHub에 코드가 이미 푸시되어 있으므로:**

```bash
# 현재 프로젝트 설정
gcloud config set project $PROJECT_ID

# Cloud Build로 빌드 및 배포
gcloud builds submit --config cloudbuild.yaml

# 또는 간단하게:
gcloud run deploy product-matcher \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-secrets=GCP_SERVICE_ACCOUNT=gcp-service-account:latest
```

#### 방법 2: 수동 배포 (Docker 직접 빌드)

```bash
# Docker 이미지 빌드
docker build -t gcr.io/$PROJECT_ID/product-matcher .

# Container Registry에 푸시
docker push gcr.io/$PROJECT_ID/product-matcher

# Cloud Run에 배포
gcloud run deploy product-matcher \
  --image gcr.io/$PROJECT_ID/product-matcher \
  --region asia-northeast3 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10
```

---

### 5단계: 환경 변수 및 Secret 마운트

```bash
# Secret을 환경 변수로 마운트
gcloud run services update product-matcher \
  --region asia-northeast3 \
  --set-secrets=GCP_SERVICE_ACCOUNT=gcp-service-account:latest
```

**또는 파일로 마운트:**

```bash
gcloud run services update product-matcher \
  --region asia-northeast3 \
  --update-secrets=/app/config/Google\ Sheets\ API.json=gcp-service-account:latest
```

---

### 6단계: 배포 확인

배포 완료 후 다음과 같은 URL이 생성됩니다:

```
Service URL: https://product-matcher-xxxxxxxxxxxx-an.a.run.app
```

이 URL로 접속하면 앱이 실행됩니다!

**URL 확인:**
```bash
gcloud run services describe product-matcher \
  --region asia-northeast3 \
  --format='value(status.url)'
```

---

## 🔧 로컬에서 Docker 테스트

배포 전에 로컬에서 테스트:

```bash
# Docker 이미지 빌드
docker build -t product-matcher .

# 로컬에서 실행 (Secret 마운트)
docker run -p 8080:8080 \
  -v "$(pwd)/config:/app/config" \
  product-matcher

# 브라우저에서 접속
# http://localhost:8080
```

---

## 💰 비용 계산

### 무료 tier (매월):
- 200만 요청
- 360,000 GB-초 (메모리 사용량)
- 180,000 vCPU-초

### 예상 비용 (무료 tier 초과 시):
- **1GB 메모리, 1 CPU 기준:**
  - 메모리: $0.00000250 / GB-초
  - CPU: $0.00002400 / vCPU-초
  - 요청: $0.40 / 백만 요청

**예시:** 100명이 하루 10분씩 사용
- 월 사용 시간: 100 × 10분 × 30일 = 30,000분 = 500시간
- 월 비용: 약 $4-5 (무료 tier 포함 시)

**실제로는 거의 무료로 사용 가능!**

---

## 📊 모니터링

### Cloud Run 대시보드
https://console.cloud.google.com/run

여기서 확인 가능:
- 요청 수
- 응답 시간
- 에러 로그
- 리소스 사용량

### 로그 확인
```bash
gcloud run logs read product-matcher \
  --region asia-northeast3 \
  --limit 50
```

---

## 🔄 업데이트 배포

코드 수정 후:

```bash
# 다시 배포 (자동으로 새 버전 생성)
gcloud run deploy product-matcher \
  --source . \
  --region asia-northeast3
```

**또는 GitHub에서 자동 배포:**

Cloud Build 트리거 설정:
1. Cloud Build → 트리거 → **트리거 만들기**
2. GitHub 연결
3. 푸시할 때마다 자동 배포

---

## ❌ 서비스 삭제

```bash
# Cloud Run 서비스 삭제
gcloud run services delete product-matcher \
  --region asia-northeast3

# Secret 삭제
gcloud secrets delete gcp-service-account

# 컨테이너 이미지 삭제
gcloud container images delete gcr.io/$PROJECT_ID/product-matcher
```

---

## 🆘 문제 해결

### 에러: Permission Denied
```bash
# 권한 추가
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/run.admin"
```

### 에러: Secret not found
```bash
# Secret 확인
gcloud secrets list

# Secret 버전 확인
gcloud secrets versions list gcp-service-account
```

### 배포 느림
- Cloud Build 로그 확인: https://console.cloud.google.com/cloud-build
- 첫 배포는 5-10분 소요 (이미지 빌드)
- 이후 배포는 2-3분

---

## ✅ 배포 완료 체크리스트

- [ ] Google Cloud 프로젝트 생성
- [ ] API 활성화 (Cloud Run, Cloud Build, Secret Manager)
- [ ] Secret Manager에 Google Sheets API 키 저장
- [ ] Docker 이미지 빌드
- [ ] Cloud Run 배포
- [ ] URL로 접속 확인
- [ ] Google Sheets 공유 (Service Account에게)

---

## 📞 도움이 필요하면

- Google Cloud 공식 문서: https://cloud.google.com/run/docs
- Streamlit Cloud Run 가이드: https://docs.streamlit.io/deploy/streamlit-cloud
- GitHub Issues: https://github.com/spica13111-netizen/newfacematch
