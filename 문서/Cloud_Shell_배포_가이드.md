# Cloud Shell을 통한 배포 가이드

## 🚀 Cloud Shell에서 배포하기

Cloud Shell은 Google Cloud에서 제공하는 무료 온라인 터미널입니다. 별도의 설치 없이 웹 브라우저에서 바로 사용할 수 있습니다.

---

## 📝 단계별 가이드

### 1단계: Cloud Shell 열기

1. **Google Cloud Console** 접속: https://console.cloud.google.com
2. 우측 상단의 **Cloud Shell 활성화** 버튼 클릭 (터미널 아이콘 `>_`)
3. 화면 하단에 터미널이 나타납니다

### 2단계: 배포 스크립트 실행

Cloud Shell 터미널에 다음 명령어를 **복사해서 붙여넣기** 후 Enter:

```bash
curl -O https://raw.githubusercontent.com/spica13111-netizen/newfacematch/main/scripts/deploy_from_cloudshell.sh
chmod +x deploy_from_cloudshell.sh
./deploy_from_cloudshell.sh
```

> **참고**: 위 명령어가 작동하지 않으면 아래 **대체 방법**을 사용하세요.

---

## 🔄 대체 방법 (GitHub 스크립트가 없는 경우)

Cloud Shell 터미널에 다음 명령어를 **한 줄씩** 복사해서 실행:

```bash
# 1. 프로젝트 설정
gcloud config set project project-3734f652-cb10-47ac-8f3

# 2. GitHub에서 코드 클론
git clone https://github.com/spica13111-netizen/newfacematch.git
cd newfacematch

# 3. Cloud Run에 배포
gcloud run deploy product-matcher \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-secrets="GCP_SERVICE_ACCOUNT=gcp-service-account:latest" \
  --project project-3734f652-cb10-47ac-8f3
```

### 3단계: 배포 완료 대기

- 배포는 **5-10분** 정도 걸립니다
- 진행 상황이 실시간으로 표시됩니다
- 완료되면 **서비스 URL**이 표시됩니다 (예: `https://product-matcher-xxxxx-an.a.run.app`)

### 4단계: 앱 접속

- 표시된 URL을 복사하여 브라우저에서 열기
- 앱이 정상적으로 작동하는지 확인

---

## ⚠️ 주의사항

### 빌드 승인 요구 시

배포 중에 다음과 같은 메시지가 나타날 수 있습니다:

```
Deploying from source requires an Artifact Registry Docker repository...
Do you want to continue (Y/n)?
```

→ **Y** 입력 후 Enter

### 로그인 요구 시

```
You are not currently authenticated...
```

→ 화면에 표시된 링크를 클릭하여 Google 계정으로 로그인

---

## 🎯 배포 성공 확인

배포가 성공하면 다음과 같은 메시지가 표시됩니다:

```
Service [product-matcher] revision [product-matcher-00001-xxx] has been deployed and is serving 100 percent of traffic.
Service URL: https://product-matcher-xxxxx-an.a.run.app
```

이 URL을 복사하여 브라우저에서 접속하세요! 🎉

---

## 🔧 문제 해결

### 오류: "Permission denied"

```bash
gcloud auth login
```

실행 후 Google 계정으로 로그인

### 오류: "Repository not found"

- GitHub 저장소가 public인지 확인
- 또는 로컬 파일 업로드 방법 사용 (아래 참고)

### 로컬 파일 직접 업로드하기

GitHub 클론 대신 로컬 파일을 Cloud Shell에 업로드:

1. Cloud Shell 터미널에서 우측 상단 **⋮** (점 3개) 클릭
2. **업로드** 선택
3. 프로젝트 폴더의 모든 파일 선택하여 업로드
4. 업로드 완료 후:

```bash
gcloud config set project project-3734f652-cb10-47ac-8f3
cd ~  # 업로드한 파일이 있는 위치로 이동
ls    # 파일 확인

# 배포 실행
gcloud run deploy product-matcher \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-secrets="GCP_SERVICE_ACCOUNT=gcp-service-account:latest" \
  --project project-3734f652-cb10-47ac-8f3
```

---

## 📞 추가 도움

배포 후 문제가 발생하면:

1. **Cloud Run 로그 확인**: https://console.cloud.google.com/run
2. **서비스 클릭** → **로그** 탭에서 오류 확인

---

## ✅ 완료!

Cloud Shell을 사용하면 로컬 환경 설정 없이도 간편하게 배포할 수 있습니다! 🚀
