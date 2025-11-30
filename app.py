"""
상품 매칭 프로그램 - Streamlit UI
구글 스프레드시트와 엑셀 파일을 연동하여 상품명 자동 매칭
"""
import os
import sys
import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image

# src 모듈 import
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.utils import (
    get_gspread_client,
    load_matching_sheet_orders,
    load_excel_products,
    update_matching_result,
    get_matching_sheet_headers,
    get_spreadsheet_url,
    batch_update_matching_results
)
from src.matcher import find_matching_products, auto_match_products
from src.image_handler import download_and_resize_image, validate_image_url
from src.excel_processor import remove_images_from_xlsx


# 페이지 설정
st.set_page_config(
    page_title="상품 매칭 프로그램",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .product-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    .match-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .match-card:hover {
        background: #e9ecef;
        border-color: #667eea;
    }
    .similarity-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .order-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    .match-info {
        flex: 1;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def init_gspread_client():
    """구글 시트 클라이언트 초기화 (캐싱)"""
    try:
        return get_gspread_client(), None
    except Exception as e:
        return None, str(e)


def display_image_from_url(image_url, width=100):
    """URL에서 이미지 다운로드하여 표시"""
    if not validate_image_url(image_url):
        st.write("이미지 없음")
        return

    try:
        image_bytes = download_and_resize_image(image_url, size=(width, width))
        if image_bytes:
            image = Image.open(BytesIO(image_bytes))
            st.image(image, width=width)
        else:
            st.write("이미지 로드 실패")
    except Exception as e:
        st.write(f"오류: {str(e)}")


def show_spreadsheet_viewer(client):
    """스프레드시트 실시간 보기 페이지"""
    st.title("📊 스프레드시트 실시간 보기")
    st.markdown("---")

    if not client:
        st.error("구글 시트에 연결할 수 없습니다.")
        return

    # 시트 선택
    sheet_tabs = st.tabs(["시트1 (주문 데이터)", "매칭상품"])

    # 시트1 탭
    with sheet_tabs[0]:
        st.subheader("📋 주문 데이터 (시트1)")
        try:
            orders_df = load_matching_sheet_orders(client, sheet_name="상품매칭용시트")
            if not orders_df.empty:
                st.dataframe(orders_df, use_container_width=True, height=600)
                st.info(f"총 {len(orders_df)}개의 주문")
            else:
                st.info("주문 데이터가 없습니다.")
        except Exception as e:
            st.error(f"오류: {str(e)}")

        if st.button("🔄 새로고침", key="refresh_sheet1"):
            st.rerun()

    # 매칭상품 탭
    with sheet_tabs[1]:
        st.subheader("✅ 매칭된 상품")
        try:
            spreadsheet = client.open("상품매칭용시트")
            try:
                worksheet = spreadsheet.worksheet("매칭상품")
                data = worksheet.get_all_values()

                if data and len(data) > 1:
                    headers = data[0]
                    rows = data[1:]
                    matched_df = pd.DataFrame(rows, columns=headers)
                    st.dataframe(matched_df, use_container_width=True, height=600)
                    st.info(f"총 {len(matched_df)}개의 매칭 완료")
                else:
                    st.info("매칭된 상품이 없습니다.")
            except:
                st.info("매칭상품 시트가 아직 생성되지 않았습니다.")
        except Exception as e:
            st.error(f"오류: {str(e)}")

        if st.button("🔄 새로고침", key="refresh_matched"):
            st.rerun()


def main():
    # 세션 상태 초기화
    if 'matched_orders' not in st.session_state:
        st.session_state['matched_orders'] = set()
    if 'excel_data' not in st.session_state:
        st.session_state['excel_data'] = None
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "매칭"

    # 구글 시트 초기화 (먼저 실행)
    client, error = init_gspread_client()

    # 페이지 선택
    page = st.sidebar.radio(
        "페이지 선택",
        ["🔗 상품 매칭", "📊 스프레드시트 보기"],
        index=0 if st.session_state['current_page'] == "매칭" else 1
    )

    if page == "📊 스프레드시트 보기":
        st.session_state['current_page'] = "보기"
        show_spreadsheet_viewer(client)
        return

    st.session_state['current_page'] = "매칭"
    st.title("🔗 상품 매칭 프로그램")
    st.markdown("---")

    # =================================================================
    # 사이드바: 엑셀 파일 업로드
    # =================================================================
    with st.sidebar:
        st.header("⚙️ 설정")
        st.markdown("---")

        # 스프레드시트 바로가기
        st.subheader("🔗 스프레드시트")
        if client and not error:
            spreadsheet_url = get_spreadsheet_url(client, "상품매칭용시트")
            if spreadsheet_url:
                st.markdown(f"[📊 스프레드시트 바로가기]({spreadsheet_url})")
            else:
                st.info("스프레드시트 URL을 가져올 수 없습니다")
        else:
            st.info("구글 시트 연결 필요")

        st.markdown("---")

        # 엑셀 파일 업로드
        st.subheader("📁 엑셀 파일 업로드")
        uploaded_file = st.file_uploader(
            "상품 마스터 엑셀 파일",
            type=['xlsx', 'xls'],
            help="전체 상품 정보가 담긴 엑셀 파일을 업로드하세요"
        )

        if uploaded_file:
            if st.session_state['excel_data'] is None:
                with st.spinner("엑셀 파일 처리 중..."):
                    try:
                        # temp 폴더 생성 (없으면)
                        temp_dir = "temp"
                        if not os.path.exists(temp_dir):
                            os.makedirs(temp_dir)

                        # 원본 파일 임시 저장
                        original_temp_path = os.path.join(temp_dir, f"original_{uploaded_file.name}")
                        with open(original_temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # 이미지 제거된 파일 경로
                        clean_temp_path = os.path.join(temp_dir, f"clean_{uploaded_file.name}")

                        # 이미지 제거 (엑셀 파일인 경우에만)
                        if uploaded_file.name.lower().endswith(('.xlsx', '.xlsm')):
                            try:
                                remove_images_from_xlsx(original_temp_path, clean_temp_path, remove_drawings=True)
                                final_path = clean_temp_path
                            except Exception as img_err:
                                # 이미지 제거 실패 시 원본 사용
                                st.warning(f"⚠️ 이미지 제거 실패. 원본 파일 사용: {str(img_err)}")
                                final_path = original_temp_path
                        else:
                            final_path = original_temp_path

                        # 엑셀 데이터 로드
                        excel_data = load_excel_products(final_path, exclude_tabs=['월말재고현황'])
                        st.session_state['excel_data'] = excel_data

                        # 임시 파일 삭제 (안전하게 처리)
                        import time
                        time.sleep(0.1)  # 파일이 완전히 닫힐 때까지 대기

                        for path_to_delete in [original_temp_path, clean_temp_path]:
                            try:
                                if os.path.exists(path_to_delete):
                                    os.remove(path_to_delete)
                            except PermissionError:
                                # 파일 삭제 실패해도 계속 진행
                                pass

                        st.success(f"✅ {len(excel_data)}개 탭 로드 완료!")

                    except Exception as e:
                        st.error(f"❌ 엑셀 로드 오류: {str(e)}")
                        # 오류 발생 시에도 임시 파일 삭제 시도
                        for path_to_delete in [original_temp_path, clean_temp_path]:
                            try:
                                if 'path_to_delete' in locals() and os.path.exists(path_to_delete):
                                    os.remove(path_to_delete)
                            except:
                                pass
            else:
                st.success(f"✅ {len(st.session_state['excel_data'])}개 탭 로드됨")

        st.markdown("---")
        st.subheader("🔧 매칭 설정")
        similarity_threshold = st.slider(
            "최소 유사도 (%)",
            min_value=30,
            max_value=100,
            value=70,
            step=5,
            help="이 값보다 낮은 유사도는 표시하지 않습니다"
        )
        top_n = st.slider(
            "추천 상품 개수",
            min_value=3,
            max_value=10,
            value=5,
            help="각 주문당 표시할 추천 상품 개수"
        )

        st.markdown("---")
        if st.button("🔄 새로고침", use_container_width=True):
            st.cache_resource.clear()
            st.session_state['excel_data'] = None
            st.session_state['matched_orders'] = set()
            st.rerun()

    # =================================================================
    # 메인: 구글 시트 연결 및 매칭
    # =================================================================

    if error:
        st.error(f"❌ 구글 API 인증 오류: {error}")
        st.info("💡 config 폴더에 Google Sheets API JSON 파일이 있는지 확인하세요.")
        st.stop()

    st.success("✅ 구글 시트 연결 완료")

    # 엑셀 데이터 체크
    if not st.session_state['excel_data']:
        st.warning("⚠️ 먼저 사이드바에서 엑셀 파일을 업로드하세요.")
        st.stop()

    st.markdown("---")

    # 스프레드시트에서 주문 데이터 로드
    with st.spinner("📋 주문 데이터 로딩 중..."):
        try:
            orders_df = load_matching_sheet_orders(client, sheet_name="상품매칭용시트")

            if orders_df.empty:
                st.info("ℹ️ 주문 데이터가 없습니다.")
                st.stop()

        except Exception as e:
            st.error(f"❌ 스프레드시트 로드 오류: {str(e)}")
            st.stop()

    # 자동 매칭 시도 (일괄 처리로 API 호출 최소화)
    auto_match_results = []
    with st.spinner("🤖 자동 매칭 중..."):
        for idx, order_row in orders_df.iterrows():
            # 이미 매칭된 주문은 건너뛰기
            if idx in st.session_state['matched_orders']:
                continue

            order_product_name = order_row.get('상품명', '')
            if not order_product_name or pd.isna(order_product_name):
                continue

            # 자동 매칭 시도
            matched_info, match_type = auto_match_products(
                order_product_name,
                st.session_state['excel_data']
            )

            if matched_info and match_type:
                # 매칭 성공 - 결과 저장 (나중에 일괄 업데이트)
                matched_data = {
                    '상품명': matched_info['상품명'],
                    '매입': matched_info['입고가계'],
                    '매출': matched_info['공급가(V+) 배송비 포함'],
                    '매입(업체)': matched_info['운영사'],
                    '탭': matched_info['탭'],
                    '옵션': matched_info.get('옵션', '')
                }

                auto_match_results.append({
                    'row_index': idx + 2,  # 헤더 제외
                    'data': matched_data,
                    'match_type': match_type,
                    'matching_log': matched_info.get('매칭로그', {}),
                    'idx': idx
                })

    # 일괄 업데이트 실행
    if auto_match_results:
        with st.spinner(f"📝 {len(auto_match_results)}개 상품 업데이트 중..."):
            success_count = batch_update_matching_results(
                client,
                "상품매칭용시트",
                auto_match_results
            )

            # 세션 상태 업데이트
            for result in auto_match_results:
                st.session_state['matched_orders'].add(result['idx'])

            if success_count > 0:
                st.success(f"✅ 자동 매칭 완료: {success_count}개 상품")

                # 매칭 상세 로그 표시
                with st.expander("🔍 자동 매칭 상세 로그"):
                    for result in auto_match_results:
                        matching_log = result.get('matching_log', {})
                        if matching_log:
                            st.markdown(f"**{result['data']['상품명']}** ({result['match_type']})")
                            for field, method in matching_log.items():
                                st.text(f"  • {field}: {method}")
                            st.markdown("---")

                st.rerun()

    # 매칭 안 된 주문만 필터링
    unmatched_orders = orders_df[~orders_df.index.isin(st.session_state['matched_orders'])]

    if unmatched_orders.empty:
        st.success("🎉 모든 주문이 매칭되었습니다!")
        st.stop()

    st.info(f"📦 매칭 대기 중인 주문: **{len(unmatched_orders)}개**")
    st.markdown("---")

    # =================================================================
    # 각 주문별 매칭 UI
    # =================================================================
    for idx, order_row in unmatched_orders.iterrows():
        order_product_name = order_row.get('상품명', '')

        if not order_product_name or pd.isna(order_product_name):
            continue

        # 주문 정보 표시
        st.markdown(f"""
            <div class="product-card">
                <div class="order-title">📦 주문 상품: {order_product_name}</div>
            </div>
        """, unsafe_allow_html=True)

        # 유사 상품 검색
        with st.spinner(f"'{order_product_name}' 매칭 중..."):
            matches = find_matching_products(
                order_product_name,
                st.session_state['excel_data'],
                top_n=top_n,
                threshold=similarity_threshold
            )

        if not matches:
            st.warning(f"⚠️ '{order_product_name}'와 유사한 상품을 찾지 못했습니다.")
            st.markdown("---")
            continue

        st.success(f"✨ {len(matches)}개의 유사 상품을 찾았습니다!")

        # 매칭 결과 표시
        for match_idx, match in enumerate(matches):
            col1, col2, col3 = st.columns([1, 5, 2])

            with col1:
                # 이미지 표시
                image_url = match.get('대표 1', '')
                if image_url and validate_image_url(image_url):
                    display_image_from_url(image_url, width=100)
                else:
                    st.write("🖼️")

            with col2:
                # 상품 정보
                st.markdown(f"""
                    <div style="padding: 0.5rem 0;">
                        <strong style="font-size: 1.1rem; color: #2d3748;">{match['상품명']}</strong><br>
                        <span class="similarity-badge">유사도: {match['유사도']}%</span><br>
                        <small style="color: #718096;">
                            📂 탭: {match['탭']} |
                            💰 입고: {match['입고가계']} |
                            💵 공급가: {match['공급가(V+) 배송비 포함']} |
                            🏢 업체: {match['운영사']}
                        </small>
                    </div>
                """, unsafe_allow_html=True)

            with col3:
                # 매칭 버튼
                if st.button(
                    "✅ 매칭하기",
                    key=f"match_{idx}_{match_idx}",
                    use_container_width=True
                ):
                    with st.spinner("매칭 중..."):
                        # 매칭 데이터 준비
                        matched_data = {
                            '상품명': match['상품명'],
                            '매입': match['입고가계'],
                            '매출': match['공급가(V+) 배송비 포함'],
                            '매입(업체)': match['운영사'],
                            '탭': match['탭'],
                            '옵션': match.get('옵션', '')
                        }

                        # 스프레드시트 업데이트 (idx + 2: 헤더 제외)
                        success = update_matching_result(
                            client,
                            "상품매칭용시트",
                            idx + 2,
                            matched_data,
                            match_type="수동매칭"
                        )

                        if success:
                            st.success(f"✅ '{order_product_name}' 매칭 완료!")
                            st.session_state['matched_orders'].add(idx)
                            st.rerun()
                        else:
                            st.error("❌ 매칭 실패. 다시 시도해주세요.")

            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")

    # 푸터
    st.markdown("""
        <div style="text-align: center; color: #718096; padding: 2rem 0; margin-top: 3rem;">
            <small>🔗 상품 매칭 프로그램 v2.0 - Powered by Streamlit</small>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
