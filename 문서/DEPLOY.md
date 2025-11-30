# Streamlit Cloud 배포 가이드

## 📋 준비사항

1. **GitHub 계정** - 이미 GitHub 설치되어 있음 ✅
2. **Google Service Account JSON** - config 폴더에 있음 ✅
3. **Streamlit Cloud 계정** (무료) - 아래에서 생성

---

## 🚀 배포 단계

### 1단계: GitHub에 코드 업로드

#### 1-1. GitHub에서 새 Repository 생성
1. [GitHub](https://github.com) 접속 및 로그인
2. 우측 상단 `+` 버튼 → `New repository` 클릭
3. Repository 정보 입력:
   - **Repository name**: `product-matching-app` (원하는 이름)
   - **Description**: 상품 매칭 프로그램
   - **Public** 또는 **Private** 선택
     - Public: 누구나 코드 볼 수 있음 (무료)
     - Private: 본인만 볼 수 있음 (Streamlit Cloud에서는 GitHub 연동으로 접근 가능)
4. **Create repository** 클릭

#### 1-2. 로컬 코드를 GitHub에 푸시
터미널에서 다음 명령어 실행:

```bash
# 현재 프로젝트 폴더에서 실행
git add .
git commit -m "Initial commit: 상품 매칭 프로그램"

# GitHub repository URL로 변경 (위에서 생성한 repo의 URL)
git remote add origin https://github.com/당신의유저명/product-matching-app.git
git branch -M main
git push -u origin main
```

---

### 2단계: Streamlit Cloud 설정

#### 2-1. Streamlit Cloud 계정 생성
1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. **Sign up with GitHub** 클릭 → GitHub 계정으로 로그인
3. GitHub 연동 승인

#### 2-2. 앱 배포
1. Streamlit Cloud 대시보드에서 **New app** 클릭
2. 배포 설정:
   - **Repository**: `당신의유저명/product-matching-app` 선택
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. **Advanced settings** 클릭

#### 2-3. Secrets 설정 (중요!)
**Advanced settings** → **Secrets** 탭에서 아래 내용 입력:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/service_accounts/v1/metadata/x509/your-service-account%40project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

**Secrets 내용 복사 방법:**
1. 로컬 `config/Google Sheets API.json` 파일 열기
2. 파일 내용 전체를 아래 형식으로 변환:

**원본 JSON:**
```json
{
  "type": "service_account",
  "project_id": "abc-123",
  ...
}
```

**Secrets에 입력할 TOML 형식:**
```toml
[gcp_service_account]
type = "service_account"
project_id = "abc-123"
...
```

> **주의**: `private_key`는 여러 줄이므로 `\n`으로 연결하여 한 줄로 입력하거나, TOML 멀티라인 문자열 사용:
```toml
private_key = """-----BEGIN PRIVATE KEY-----
여기에 실제 키 내용
-----END PRIVATE KEY-----
"""
```

#### 2-4. 배포 시작
1. **Deploy!** 버튼 클릭
2. 배포 진행 상황 확인 (1-2분 소요)
3. 완료되면 앱 URL 생성 (예: `https://your-app.streamlit.app`)

---

### 3단계: 앱 사용

배포 완료 후:
1. 생성된 URL 접속
2. 다른 사람에게 URL 공유 → 누구나 접속 가능!
3. Google Sheets 접근 권한:
   - Google Sheets API의 Service Account 이메일에 스프레드시트 공유 필요
   - 스프레드시트 → 공유 → Service Account 이메일 추가 (편집 권한)

---

## 🔧 문제 해결

### Secrets 오류
- **에러**: `Google API JSON 파일을 찾을 수 없습니다`
- **해결**: Streamlit Cloud → Settings → Secrets에서 `gcp_service_account` 제대로 입력했는지 확인

### 스프레드시트 접근 불가
- **에러**: `Spreadsheet not found`
- **해결**: Google Sheets를 Service Account 이메일과 공유했는지 확인
  - Service Account 이메일: JSON의 `client_email` 필드

### 앱 업데이트
코드 수정 후:
```bash
git add .
git commit -m "업데이트 내용"
git push
```
→ Streamlit Cloud가 자동으로 재배포

---

## 📞 도움이 필요하면

- [Streamlit 공식 문서](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [Streamlit Secrets 가이드](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
