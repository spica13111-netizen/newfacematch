# 상품 매칭 프로그램

Google Sheets와 Excel 파일을 연동하여 상품명을 자동으로 매칭하는 Streamlit 기반 웹 프로그램입니다.

## 🚀 빠른 시작

### 📖 가이드 문서
- **처음 사용자**: `⭐ 처음 사용하기.txt`
- **빠른 참고**: [문서/Quick_Start.md](문서/Quick_Start.md)
- **Cloud 배포**: [문서/Cloud_Run_배포_가이드.md](문서/Cloud_Run_배포_가이드.md)

### 1️⃣ 설치 (처음 한 번만)
```bash
💊 패키지 설치.bat
```

### 2️⃣ 실행 방법

#### 로컬 실행 (PC에서만)
```bash
💻 로컬 실행.bat
```

#### 임시 웹 공유 (ngrok)
```bash
🌐 웹으로 시작.bat
```
- URL 매번 변경
- PC 꺼지면 접속 불가

#### 영구 웹 배포 (Google Cloud Run)
```bash
배포파일\🚀 Cloud Run 배포.bat
```
- 고정 URL
- 항상 접속 가능
- 무료 티어 제공

## 📁 폴더 구조

```
프로젝트/
├── 💻 로컬 실행.bat           # 로컬 실행
├── 🌐 웹으로 시작.bat         # ngrok 임시 웹 공유
├── 💊 패키지 설치.bat         # 패키지 설치
├── app.py                    # 메인 프로그램
├── requirements.txt          # 패키지 목록
├── Dockerfile                # Docker 설정
├── cloudbuild.yaml           # Cloud Build 설정
├── config/                   # Google API 설정
│   └── Google Sheets API.json (보안: gitignore)
├── src/                      # 소스 코드
│   ├── utils.py              # Google Sheets/Excel 유틸
│   ├── matcher.py            # 상품 매칭 로직
│   ├── image_handler.py      # 이미지 처리
│   └── excel_processor.py    # Excel 처리
├── scripts/                  # 배포 스크립트
│   ├── setup_cloud_build.bat # Cloud Build 설정
│   └── upload_secret.bat     # Secret Manager 업로드
├── 배포파일/                 # 배포 관련 파일
│   └── 🚀 Cloud Run 배포.bat # Cloud Run 수동 배포
└── 문서/                     # 문서
    ├── Quick_Start.md        # 빠른 시작 가이드
    └── Cloud_Run_배포_가이드.md # Cloud 배포 상세
```

## 📋 주요 기능

### 자동 매칭
- ✅ **2단계 자동 매칭**: 100% 일치 → 모델명 100% 일치
- ✅ **Fuzzy matching**: 유사도 기반 추천 (상위 3-10개)
- ✅ **실시간 업데이트**: Google Sheets 자동 반영

### 데이터 처리
- ✅ Google Sheets 실시간 연동
- ✅ 다중 탭 Excel 파일 지원
- ✅ Excel 이미지 자동 제거 (용량 최적화)
- ✅ 이미지 URL 미리보기

### 배포 옵션
- ✅ 로컬 실행
- ✅ ngrok 임시 웹 공유
- ✅ Google Cloud Run 영구 배포
- ✅ GitHub 자동 배포 지원

## 🌐 배포 방법

### 1. 로컬 실행
```bash
💻 로컬 실행.bat
```

### 2. 임시 웹 공유 (ngrok)
```bash
🌐 웹으로 시작.bat
```

### 3. 영구 배포 (Cloud Run)
상세 가이드: [문서/Cloud_Run_배포_가이드.md](문서/Cloud_Run_배포_가이드.md)

#### 수동 배포
```bash
배포파일\🚀 Cloud Run 배포.bat
```

#### 자동 배포 (GitHub)
```bash
git add .
git commit -m "Update"
git push origin main
```
→ 자동으로 Cloud Run에 배포됨!

## 🔧 설정

### 필수 설정
1. `config/Google Sheets API.json` 추가
2. Google Service Account로 스프레드시트 공유
3. 패키지 설치: `💊 패키지 설치.bat`

### Cloud Run 배포 시 추가 설정
1. Google Cloud 프로젝트 생성
2. gcloud CLI 설치
3. Secret Manager에 인증 정보 업로드

자세한 내용: [문서/Cloud_Run_배포_가이드.md](문서/Cloud_Run_배포_가이드.md)

## ⚡ Cloud Run 빠른 배포 가이드

### 전제 조건
- Google Cloud 계정 (무료 티어 사용 가능)
- gcloud CLI 설치: https://cloud.google.com/sdk/docs/install

### 1단계: Google Cloud 설정

```bash
# gcloud CLI 로그인
gcloud auth login

# 프로젝트 ID 설정 (콘솔에서 확인)
gcloud config set project YOUR_PROJECT_ID

# 필요한 API 활성화
scripts\setup_cloud_build.bat
```

### 2단계: Secret Manager 업로드

```bash
# Google Sheets API JSON을 Secret Manager에 업로드
scripts\upload_secret.bat
```

입력값:
- Secret 이름: `gcp-service-account`
- JSON 파일 경로: `config/Google Sheets API.json`

### 3단계: Cloud Shell에서 배포

1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. Cloud Shell 열기 (화면 우측 상단 터미널 아이콘)
3. 다음 명령어 실행:

```bash
# 배포 스크립트 다운로드 및 실행
curl -O https://raw.githubusercontent.com/spica13111-netizen/newfacematch/main/scripts/deploy_from_cloudshell.sh
chmod +x deploy_from_cloudshell.sh
./deploy_from_cloudshell.sh
```

### 4단계: 자동 배포 설정 (선택)

GitHub에 푸시할 때 자동으로 배포:

1. [Cloud Build](https://console.cloud.google.com/cloud-build/triggers) 접속
2. "트리거 만들기" 클릭
3. GitHub 저장소 연결: `spica13111-netizen/newfacematch`
4. 브랜치: `main`
5. 구성: "Cloud Build 구성 파일" → `cloudbuild.yaml`
6. 저장

이제 `git push`만 하면 자동 배포! 🚀

## ❓ 트러블슈팅

### 🔴 Error: "Dockerfile not found"
**원인**: Dockerfile이 없거나 잘못된 위치
**해결**:
```bash
# Dockerfile이 있는지 확인
dir Dockerfile

# 없으면 backup에서 복사
copy Dockerfile.backup Dockerfile
```

### 🔴 Cloud Build 타임아웃
**원인**: 이미지 빌드 시간 초과
**해결**: `cloudbuild.yaml`에 타임아웃 설정 확인
```yaml
timeout: '1800s'  # 30분
```

### 🔴 Secret Manager 에러
**원인**: GCP Service Account JSON이 없음
**해결**:
```bash
# Secret 업로드 확인
gcloud secrets list

# 재업로드
scripts\upload_secret.bat
```

### 🔴 포트 연결 실패
**원인**: Cloud Run 포트 설정 오류
**해결**: `.streamlit/config.toml`에서 headless 모드 확인
```toml
[server]
headless = true
```

### 🔴 메모리 부족
**원인**: Excel 파일이 너무 큼
**해결**: `cloudbuild.yaml`에서 메모리 증가
```yaml
- '--memory'
- '2Gi'  # 1Gi → 2Gi로 변경
```


## 🛠️ 기술 스택

- **Frontend/Backend**: Streamlit
- **Google API**: gspread, google-auth
- **데이터 처리**: pandas, openpyxl
- **매칭**: rapidfuzz (Fuzzy matching)
- **이미지**: Pillow, requests
- **배포**: Docker, Google Cloud Run
- **CI/CD**: Cloud Build, GitHub

## 📞 문의

- **GitHub**: https://github.com/spica13111-netizen/newfacematch
- **Issues**: 버그 리포트 및 기능 제안

## 📄 라이선스

MIT License
