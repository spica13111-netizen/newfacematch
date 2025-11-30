# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY app.py .
COPY src/ ./src/
COPY .streamlit/ ./.streamlit/
# config/ 폴더는 Secret Manager에서 제공되므로 복사하지 않음

# Streamlit 설정
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 포트 노출
EXPOSE 8080

# 헬스체크
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Streamlit 실행
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
