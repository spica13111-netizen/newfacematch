# 빠른 시작 가이드

## 🎯 목적별 실행 방법

### 1. 로컬에서만 사용 (PC에서만)
```
💻 로컬 실행.bat (더블클릭)
```
→ 브라우저가 자동으로 열립니다

---

### 2. 친구에게 임시로 공유 (URL 매번 바뀜)
```
🌐 웹으로 시작.bat (더블클릭)
```
→ ngrok URL이 표시됩니다 (예: `https://abc123.ngrok-free.app`)
→ **주의:** PC를 끄면 접속 불가, URL 매번 변경

---

### 3. 영구 URL로 배포 (추천!)
#### 방법 A: 수동 배포 (빠름)
```
배포파일\🚀 Cloud Run 배포.bat (더블클릭)
```

#### 방법 B: GitHub 자동 배포 (편함)
1. `문서\Cloud_Run_배포_가이드.md` 참고
2. 설정 완료 후:
   ```bash
   git add .
   git commit -m "Update"
   git push origin main
   ```
3. 자동으로 배포됨! ✨

---

## 🔧 최초 설정 (한 번만)

### Google Cloud Run 사용 시
```
1. scripts\setup_cloud_build.bat (실행)
2. scripts\upload_secret.bat (실행)
3. Cloud Build 트리거 설정 (웹에서)
```

자세한 내용: `문서\Cloud_Run_배포_가이드.md`

---

## 📁 파일 구조

```
프로젝트/
├── 💻 로컬 실행.bat          ← PC에서만 실행
├── 🌐 웹으로 시작.bat        ← ngrok으로 임시 공유
├── 배포파일/
│   └── 🚀 Cloud Run 배포.bat ← 수동 배포
├── scripts/
│   ├── setup_cloud_build.bat ← Cloud 초기 설정
│   └── upload_secret.bat     ← 인증 파일 업로드
└── 문서/
    ├── Cloud_Run_배포_가이드.md ← 상세 설명
    └── Quick_Start.md           ← 이 파일
```

---

## 💡 추천 사용법

### 개발/테스트 중
→ `💻 로컬 실행.bat` 사용

### 친구에게 보여줄 때
→ `🌐 웹으로 시작.bat` 사용 (임시)

### 실제 운영
→ Cloud Run 배포 (영구 URL)
