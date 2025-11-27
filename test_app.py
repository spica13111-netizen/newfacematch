"""
간단한 테스트 앱 - import 문제 확인용
"""
import streamlit as st

st.title("🎉 테스트 성공!")
st.write("Streamlit Cloud가 정상 작동합니다.")

# src 모듈 import 테스트
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

    from src.utils import get_gspread_client
    st.success("✅ src.utils import 성공!")

    from src.matcher import find_matching_products
    st.success("✅ src.matcher import 성공!")

    from src.image_handler import validate_image_url
    st.success("✅ src.image_handler import 성공!")

    from src.excel_processor import remove_images_from_xlsx
    st.success("✅ src.excel_processor import 성공!")

except Exception as e:
    st.error(f"❌ Import 에러: {e}")
    import traceback
    st.code(traceback.format_exc())

# Secrets 테스트
try:
    if 'gcp_service_account' in st.secrets:
        st.success("✅ Secrets 설정 확인!")
    else:
        st.warning("⚠️ Secrets에 gcp_service_account가 없습니다.")
except Exception as e:
    st.error(f"❌ Secrets 에러: {e}")
