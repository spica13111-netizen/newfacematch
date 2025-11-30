# 프로젝트 구조 문서

## 프로젝트 개요

**상품 매칭 프로그램 v2.0**

구글 스프레드시트의 주문 데이터와 엑셀 상품 마스터를 유사도 기반으로 자동 매칭하는 시스템입니다.

---

## 폴더 구조

```
(스프레드시트)발주서 실시간/
│
├── app.py                      # 메인 Streamlit 웹 애플리케이션
├── requirements.txt            # Python 패키지 의존성
├── README.md                   # 사용 설명서
├── STRUCTURE.md                # 이 문서
│
├── run.bat                     # Windows 실행 스크립트
├── run.ps1                     # PowerShell 실행 스크립트
│
├── config/                     # 설정 파일 디렉토리
│   ├── Google Sheets API.json  # 구글 시트 API 인증
│   └── Google Drive API.json   # 구글 드라이브 API 인증 (옵션)
│
├── src/                        # 소스 코드 모듈
│   ├── __init__.py             # 패키지 초기화
│   ├── utils.py                # 유틸리티: 구글 시트/엑셀 처리
│   ├── matcher.py              # 상품명 유사도 매칭 로직
│   └── image_handler.py        # 이미지 다운로드 및 처리
│
├── docs/                       # 문서 (자동 생성)
└── logs/                       # 로그 파일 (자동 생성)
```

---

## 주요 파일 설명

### 1. app.py
**메인 Streamlit 웹 애플리케이션**

- **역할**: 사용자 인터페이스 제공
- **주요 기능**:
  - 엑셀 파일 업로드 및 로딩
  - 구글 시트 연결 및 주문 데이터 로드
  - 상품 매칭 UI 제공
  - 매칭 결과 구글 시트 업데이트
- **의존성**: `src/utils.py`, `src/matcher.py`, `src/image_handler.py`

### 2. requirements.txt
**Python 패키지 의존성**

```
google-auth              # 구글 API 인증
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
gspread                  # 구글 스프레드시트 라이브러리

pandas                   # 데이터 처리
openpyxl                 # 엑셀 파일 읽기

rapidfuzz                # 빠른 문자열 유사도 매칭

Pillow                   # 이미지 처리
requests                 # HTTP 요청

streamlit                # 웹 UI
```

### 3. src/utils.py
**구글 시트 및 엑셀 처리 유틸리티**

**주요 함수**:
- `get_service_account_file()`: config 폴더에서 JSON 인증 파일 찾기
- `get_gspread_client()`: gspread 클라이언트 생성
- `load_matching_sheet_orders()`: 구글 시트에서 주문 데이터 로드
- `load_excel_products()`: 엑셀 파일의 모든 탭 로드
- `update_matching_result()`: 매칭 결과를 [매칭상품] 탭에 업데이트
- `get_matching_sheet_headers()`: 스프레드시트 헤더 정보 가져오기

### 4. src/matcher.py
**상품명 유사도 매칭 로직**

**주요 함수**:
- `find_matching_products()`: 주문 상품명과 유사한 상품 찾기
- `batch_match_products()`: 여러 주문 일괄 매칭
- `get_best_match()`: 가장 유사한 상품 1개만 반환 (자동 매칭용)

**알고리즘**:
- `rapidfuzz.fuzz.token_set_ratio` 사용
- 단어 순서 무관, 띄어쓰기 무관
- 오타 허용

### 5. src/image_handler.py
**이미지 다운로드 및 처리**

**주요 함수**:
- `download_and_resize_image()`: URL에서 이미지 다운로드 및 리사이즈
- `get_image_base64()`: 이미지를 Base64로 인코딩
- `insert_image_to_sheet()`: 구글 시트에 이미지 삽입
- `validate_image_url()`: 이미지 URL 유효성 검사

**이미지 처리 과정**:
1. URL에서 이미지 다운로드 (requests)
2. PIL로 이미지 열기
3. 100x100 픽셀로 리사이즈
4. JPEG 형식으로 최적화
5. 구글 시트에 IMAGE 함수로 삽입

---

## 데이터 흐름

```
[사용자] → [엑셀 업로드] → [app.py]
                                ↓
                    [src/utils.py: load_excel_products()]
                                ↓
                        [엑셀 데이터 로드]
                                ↓
[구글 시트] → [src/utils.py: load_matching_sheet_orders()]
                                ↓
                        [주문 데이터 로드]
                                ↓
            [src/matcher.py: find_matching_products()]
                                ↓
                    [유사도 매칭 (rapidfuzz)]
                                ↓
                    [추천 상품 리스트 생성]
                                ↓
            [app.py: 이미지 + 상품 정보 표시]
                                ↓
                    [사용자 매칭 버튼 클릭]
                                ↓
        [src/utils.py: update_matching_result()]
                                ↓
        [src/image_handler.py: insert_image_to_sheet()]
                                ↓
            [구글 시트 [매칭상품] 탭 업데이트]
```

---

## 구글 스프레드시트 구조

### 스프레드시트 이름
`상품매칭용시트`

### 탭 구조

#### 1. 시트1 (주문 데이터 - 읽기 전용)
```
발주일자 | 구매일자 | 매입(업체) | 매출(MALL) | 주문자명 | 주문자 연락처 | 수령인 | 수령인휴대폰 | 수령인연락처 | 우편번호 | 주소 | 배송메모 | 상품명 | 수량 | 매출 | 배송비 | 매입 | M | 비고
```

**사용 컬럼**: `상품명` (필수)

#### 2. 매칭상품 (매칭 결과 - 쓰기)
```
상품명 | 매입 | 매출 | 매입(업체) | 탭 | 매칭이미지
```

**자동 생성**: 탭이 없으면 프로그램이 자동 생성

---

## 엑셀 파일 구조

### 파일 형식
`.xlsx` 또는 `.xls`

### 탭 구조
- 여러 탭 존재 (예: 가전, 생활용품, 주방용품 등)
- `[월말재고현황]` 탭은 자동 제외
- 각 탭의 **1행은 헤더**

### 필수 컬럼
```
상품명 | 입고가계 | 공급가(V+) 배송비 포함 | 운영사 | 대표 1
```

- **상품명**: 매칭할 상품 이름
- **입고가계**: 매입 가격
- **공급가(V+) 배송비 포함**: 매출 가격
- **운영사**: 매입 업체명
- **대표 1**: 상품 이미지 URL

---

## 실행 방법

### Windows
```bash
run.bat
```

### PowerShell
```powershell
.\run.ps1
```

### 직접 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 기술 스택 상세

### 프론트엔드
- **Streamlit**: Python 기반 웹 UI 프레임워크
- **HTML/CSS**: 커스텀 스타일링

### 백엔드
- **Python 3.8+**: 메인 프로그래밍 언어
- **gspread**: 구글 스프레드시트 API 래퍼
- **pandas**: 데이터프레임 처리
- **openpyxl**: 엑셀 파일 읽기

### 매칭 알고리즘
- **rapidfuzz**: 빠른 문자열 유사도 계산
- **Levenshtein 거리 기반 매칭**

### 이미지 처리
- **Pillow (PIL)**: 이미지 다운로드, 리사이즈
- **requests**: HTTP 이미지 다운로드

---

## 버전 히스토리

### v2.0 (2025-11-26)
- **완전히 새로운 시스템**
- 기존 발주서 관리 기능 제거
- 상품 매칭 시스템으로 전환
- 유사도 기반 자동 매칭
- 이미지 미리보기 지원
- 실시간 구글 시트 업데이트

### v1.0 (이전)
- 구글 발주서 자동화 프로그램
- 발주 마감 처리
- 데일리 클리닝
- 스케줄 자동화

---

## 개발 가이드

### 새 기능 추가 시
1. `src/` 폴더에 모듈 추가
2. `app.py`에서 import 및 UI 구성
3. `README.md` 업데이트
4. `STRUCTURE.md` 업데이트

### 코드 스타일
- PEP 8 준수
- 함수마다 docstring 작성
- 타입 힌트 권장 (Python 3.8+)

### 테스트
- 실제 구글 시트와 엑셀로 수동 테스트
- 유사도 매칭 알고리즘 검증

---

## 문의

프로젝트 관련 문의사항은 개발자에게 연락하세요.

**마지막 업데이트**: 2025-11-26
