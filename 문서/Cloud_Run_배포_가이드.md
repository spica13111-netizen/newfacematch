# Google Cloud Run 자동 배포 가이드

GitHub에 코드를 푸시하면 자동으로 Cloud Run에 배포되는 시스템을 설정합니다.

## 📋 사전 준비

### 필요한 것
- ✅ Google Cloud 계정 (Gmail 있으면 OK)
- ✅ Google Cloud 프로젝트
- ✅ 결제 계정 활성화 (신용카드 등록)
- ✅ gcloud CLI 설치
- ✅ GitHub 저장소: https://github.com/spica13111-netizen/newfacematch

### 무료 크레딧
- 신규 가입 시 $300 크레딧 (3개월)
- Cloud Run 무료 티어: 월 2백만 요청

---

## 🚀 배포 방법 (2가지)

### 방법 1: GitHub 자동 배포 (추천)
GitHub에 푸시하면 자동으로 배포됩니다.

### 방법 2: 수동 배포
배치 파일을 실행하여 즉시 배포합니다.

---

## 📝 방법 1: GitHub 자동 배포 설정

### 1단계: Google Cloud 프로젝트 설정

#### 1.1 프로젝트 ID 확인
```bash
gcloud config get-value project
```

또는 https://console.cloud.google.com 에서 확인

#### 1.2 API 활성화
`scripts\setup_cloud_build.bat` 실행:
```bash
scripts\setup_cloud_build.bat
```

입력 요구 시 **프로젝트 ID** 입력

**활성화되는 API:**
- Cloud Build API
- Cloud Run API
- Secret Manager API
- Container Registry API
- Artifact Registry API

---

### 2단계: Google Sheets API 인증 정보 업로드

#### 2.1 Secret Manager에 업로드
`scripts\upload_secret.bat` 실행:
```bash
scripts\upload_secret.bat
```

입력 요구 시 **프로젝트 ID** 입력

이 스크립트는 `config\Google Sheets API.json` 파일을 Secret Manager에 업로드합니다.

#### 2.2 확인
https://console.cloud.google.com/security/secret-manager 에서 `gcp-service-account` 시크릿 확인

---

### 3단계: Cloud Build 서비스 계정 권한 설정

#### 3.1 Cloud Build 서비스 계정 찾기
https://console.cloud.google.com/cloud-build/settings 접속

#### 3.2 권한 활성화
다음 권한을 **사용 설정**으로 변경:
- ✅ Cloud Run 관리자
- ✅ Service Account 사용자
- ✅ Secret Manager 보안 비밀 접근자

---

### 4단계: GitHub 저장소 연결

#### 4.1 Cloud Build 트리거 페이지 접속
https://console.cloud.google.com/cloud-build/triggers 접속

#### 4.2 트리거 만들기
1. **"트리거 만들기"** 클릭
2. **이름**: `github-auto-deploy` (원하는 이름)
3. **이벤트**: "브랜치에 푸시"
4. **소스**:
   - "저장소 연결" 클릭 → GitHub 선택
   - GitHub 계정 연결 (OAuth 인증)
   - 저장소 선택: `spica13111-netizen/newfacematch`
5. **브랜치**: `^main$` (정규식)
6. **구성**:
   - 유형: Cloud Build 구성 파일 (yaml 또는 json)
   - 위치: 저장소
   - Cloud Build 구성 파일 위치: `cloudbuild.yaml`
7. **"만들기"** 클릭

#### 4.3 변수 설정 (선택사항)
트리거 생성 후 편집에서 **대체 변수** 추가:
- `_REGION`: `asia-northeast3`

---

### 5단계: 첫 배포 테스트

#### 5.1 코드 변경 및 푸시
```bash
# 변경사항 커밋
git add .
git commit -m "Setup Cloud Build auto-deploy"
git push origin main
```

#### 5.2 배포 진행 상황 확인
https://console.cloud.google.com/cloud-build/builds 에서 빌드 진행 상황 확인

**빌드 단계:**
1. Docker 이미지 빌드
2. Container Registry에 푸시
3. Cloud Run에 배포

**예상 소요 시간:** 5-10분

#### 5.3 배포 완료 확인
빌드가 성공하면 **Service URL**이 표시됩니다.
예: `https://product-matcher-xxxxx-an.a.run.app`

---

## 📝 방법 2: 수동 배포 (빠른 테스트용)

### 수동 배포 실행
`배포파일\🚀 Cloud Run 배포.bat` 실행:
```bash
배포파일\🚀 Cloud Run 배포.bat
```

**주의:** 수동 배포도 Secret Manager 설정(2단계)이 필요합니다.

---

## 🔧 문제 해결

### 오류: "Permission denied"
→ 3단계의 Cloud Build 서비스 계정 권한을 확인하세요.

### 오류: "Secret not found"
→ 2단계의 Secret Manager 업로드를 다시 실행하세요.

### 오류: "Repository not found"
→ 4단계에서 GitHub 저장소 연결을 다시 확인하세요.

### 빌드는 성공했는데 앱이 시작되지 않음
→ Cloud Run 로그 확인:
https://console.cloud.google.com/run

### 배포 후 앱 접속 시 "Error: Service Unavailable"
→ 5-10분 정도 기다려주세요 (Cold start)

---

## 📊 배포 후 관리

### URL 확인
https://console.cloud.google.com/run → `product-matcher` 클릭 → URL 복사

### 로그 확인
https://console.cloud.google.com/run → `product-matcher` → "로그" 탭

### 비용 확인
https://console.cloud.google.com/billing

### 서비스 삭제 (배포 중단)
```bash
gcloud run services delete product-matcher --region asia-northeast3
```

---

## 🎯 자동 배포 워크플로우

1. 코드 수정
2. Git 커밋 및 푸시
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
3. Cloud Build 자동 트리거 (GitHub webhook)
4. Docker 이미지 빌드
5. Cloud Run 자동 배포
6. 새 버전 서비스 시작

**모든 과정 자동! 손댈 필요 없음!** 🎉

---

## 💡 팁

### 고정 URL 사용
배포된 URL은 변경되지 않습니다. (예: `https://product-matcher-xxxxx-an.a.run.app`)

### 커스텀 도메인 연결
https://console.cloud.google.com/run → `product-matcher` → "도메인 매핑"

### 비용 절감
- 사용하지 않을 때 자동으로 0개 인스턴스로 축소됨
- 요청이 오면 자동으로 시작 (5-10초 소요)

### 성능 최적화
- 메모리: 1Gi (필요시 2Gi로 증가)
- CPU: 1 (필요시 2로 증가)
- 최대 인스턴스: 10 (트래픽 많으면 증가)

---

## 📞 문의

문제가 발생하면:
1. Cloud Build 로그 확인
2. Cloud Run 로그 확인
3. 이 문서의 문제 해결 섹션 참고
