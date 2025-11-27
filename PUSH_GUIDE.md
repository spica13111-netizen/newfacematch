# GitHub Push 가이드

## Personal Access Token으로 인증하기

### 1단계: GitHub Token 생성

1. GitHub 로그인 (spica13111-netizen 계정)
2. [Personal Access Tokens 페이지](https://github.com/settings/tokens) 접속
   - 또는: 우측 상단 프로필 → Settings → Developer settings → Personal access tokens → Tokens (classic)
3. **Generate new token** → **Generate new token (classic)** 클릭
4. 설정:
   - **Note**: `newfacematch-deploy` (토큰 이름)
   - **Expiration**: 원하는 기간 (90 days 추천)
   - **Select scopes**: `repo` 전체 체크 ✅
5. **Generate token** 클릭
6. **생성된 토큰 복사** (한 번만 보여지므로 꼭 저장!)
   - 형식: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2단계: Git에서 Token 사용

터미널에서 아래 명령어 실행 (토큰을 붙여넣으세요):

```bash
# Remote URL을 Token 포함 형식으로 변경
git remote set-url origin https://ghp_당신의토큰@github.com/spica13111-netizen/newfacematch.git

# 푸시
git push -u origin main
```

**예시:**
```bash
git remote set-url origin https://ghp_abc123xyz456@github.com/spica13111-netizen/newfacematch.git
git push -u origin main
```

---

## 또는 방법 2: GitHub Desktop 사용 (더 쉬움)

1. [GitHub Desktop](https://desktop.github.com/) 다운로드 및 설치
2. spica13111-netizen 계정으로 로그인
3. **File → Add Local Repository**
4. 현재 프로젝트 폴더 선택
5. **Publish repository** 클릭
6. Repository 이름 확인 후 Publish

---

## 푸시 성공 확인

푸시 성공 후:
- https://github.com/spica13111-netizen/newfacematch 접속
- 코드가 올라갔는지 확인

다음 단계: Streamlit Cloud 배포 (DEPLOY.md 참고)
