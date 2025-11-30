import os
from pathlib import Path

# Streamlit 설정 디렉토리 생성
streamlit_dir = Path.home() / ".streamlit"
streamlit_dir.mkdir(exist_ok=True)

# credentials.toml 파일 생성
credentials_file = streamlit_dir / "credentials.toml"
credentials_content = """[general]
email = ""
"""

with open(credentials_file, "w", encoding="utf-8") as f:
    f.write(credentials_content)

print(f"Streamlit credentials file created: {credentials_file}")
