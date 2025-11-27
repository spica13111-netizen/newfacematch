# Configuration Files

이 폴더에는 Google API 인증 파일이 필요합니다.

## 필요한 파일

### 1. Google Sheets API.json
Google Cloud Console에서 생성한 Service Account JSON 파일

생성 방법:
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 또는 선택
3. "APIs & Services" > "Credentials" 이동
4. "Create Credentials" > "Service Account" 선택
5. Service Account 생성 후 JSON 키 다운로드
6. 다운로드한 파일을 `Google Sheets API.json`으로 저장

### 2. Streamlit Cloud 배포 시
- GitHub에는 이 파일을 업로드하지 마세요 (.gitignore에 포함됨)
- Streamlit Cloud의 Secrets 기능을 사용하여 설정하세요

**Streamlit Secrets 설정 방법:**
```toml
# .streamlit/secrets.toml 형식으로 설정
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "cert-url"
```
