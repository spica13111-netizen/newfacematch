"""
상품명 유사도 매칭 모듈
"""
from rapidfuzz import fuzz, process
import pandas as pd
import re


def normalize_string(text):
    """
    문자열 정규화 함수
    - 공백 제거
    - 특수문자 제거
    - 알파벳 소문자로 변환
    - 숫자는 유지

    Args:
        text: 정규화할 문자열

    Returns:
        str: 정규화된 문자열
    """
    if pd.isna(text) or not text:
        return ""

    text = str(text).strip()

    # 알파벳을 소문자로 변환
    text = text.lower()

    # 특수문자 제거 (한글, 영문, 숫자만 유지)
    text = re.sub(r'[^a-z0-9가-힣]', '', text)

    return text


def find_matching_products(order_product_name, excel_products, top_n=5, threshold=60):
    """
    주문 상품명과 유사한 상품을 엑셀 데이터에서 찾기

    Args:
        order_product_name: 주문서의 상품명
        excel_products: 엑셀 데이터 딕셔너리 {탭명: DataFrame}
        top_n: 반환할 상위 매칭 개수
        threshold: 최소 유사도 점수 (0-100)

    Returns:
        list: 매칭된 상품 리스트
            [
                {
                    '탭': '가전',
                    '상품명': '쿨 냉장고',
                    '유사도': 95.5,
                    '입고가계': '50000',
                    '공급가(V+) 배송비 포함': '75000',
                    '운영사': 'ABC상사',
                    '대표 1': 'http://...'
                },
                ...
            ]
    """
    if not order_product_name or pd.isna(order_product_name):
        return []

    order_product_name = str(order_product_name).strip()
    if not order_product_name:
        return []

    matches = []

    # 각 탭별로 상품명 검색
    for tab_name, df in excel_products.items():
        # 상품명 컬럼 찾기 (다양한 가능성 고려)
        product_col = None
        for col in df.columns:
            if '상품명' in str(col) or '제품명' in str(col) or 'product' in str(col).lower():
                product_col = col
                break

        if product_col is None:
            continue

        # 각 상품과 유사도 비교
        for idx, row in df.iterrows():
            excel_product_name = row.get(product_col, '')

            if pd.isna(excel_product_name) or not str(excel_product_name).strip():
                continue

            excel_product_name = str(excel_product_name).strip()

            # 유사도 계산 (token_set_ratio: 단어 순서 무관)
            similarity = fuzz.token_set_ratio(order_product_name, excel_product_name)

            # threshold 이상만 추가
            if similarity >= threshold:
                match_info = {
                    '탭': tab_name,
                    '상품명': excel_product_name,
                    '유사도': round(similarity, 1),
                    '입고가계': str(row.get('입고가계', '')),
                    '공급가(V+) 배송비 포함': str(row.get('공급가(V+) 배송비 포함', '')),
                    '운영사': str(row.get('운영사', '')),
                    '대표 1': str(row.get('대표 1', ''))
                }
                matches.append(match_info)

    # 유사도 순으로 정렬
    matches.sort(key=lambda x: x['유사도'], reverse=True)

    # 상위 N개만 반환
    return matches[:top_n]


def batch_match_products(orders_df, excel_products, top_n=5, threshold=60):
    """
    여러 주문을 일괄 매칭

    Args:
        orders_df: 주문 데이터프레임 (상품명 컬럼 필수)
        excel_products: 엑셀 데이터 딕셔너리
        top_n: 상품별 반환할 매칭 개수
        threshold: 최소 유사도 점수

    Returns:
        dict: {주문_인덱스: [매칭_리스트]}
    """
    results = {}

    for idx, row in orders_df.iterrows():
        order_product_name = row.get('상품명', '')
        matches = find_matching_products(order_product_name, excel_products, top_n, threshold)
        results[idx] = matches

    return results


def get_best_match(order_product_name, excel_products, threshold=80):
    """
    가장 유사도가 높은 상품 1개만 반환 (자동 매칭용)

    Args:
        order_product_name: 주문 상품명
        excel_products: 엑셀 데이터 딕셔너리
        threshold: 최소 유사도 점수 (높게 설정)

    Returns:
        dict or None: 가장 유사한 상품 정보 또는 None
    """
    matches = find_matching_products(order_product_name, excel_products, top_n=1, threshold=threshold)

    if matches:
        return matches[0]
    return None


def auto_match_products(order_product_name, excel_products):
    """
    자동 매칭 함수 - 파이프라인 방식
    1. 상품명 100% 일치 확인
    2. 모델명 100% 포함 확인

    Args:
        order_product_name: 주문 상품명
        excel_products: 엑셀 데이터 딕셔너리

    Returns:
        tuple: (매칭된 상품 정보 dict or None, 매칭 방식 str)
            매칭 방식: "100%일치", "모델명100%일치", None
    """
    if not order_product_name or pd.isna(order_product_name):
        return None, None

    order_product_name = str(order_product_name).strip()
    if not order_product_name:
        return None, None

    # 시트 상품명 정규화
    normalized_order = normalize_string(order_product_name)

    # 각 탭별로 검색
    for tab_name, df in excel_products.items():
        # 상품명 컬럼 찾기
        product_col = None
        for col in df.columns:
            if '상품명' in str(col) or '제품명' in str(col) or 'product' in str(col).lower():
                product_col = col
                break

        if product_col is None:
            continue

        # 모델명 컬럼 찾기
        model_col = None
        for col in df.columns:
            if '모델명' in str(col) or 'model' in str(col).lower():
                model_col = col
                break

        # 각 상품 확인
        for idx, row in df.iterrows():
            excel_product_name = row.get(product_col, '')

            if pd.isna(excel_product_name) or not str(excel_product_name).strip():
                continue

            excel_product_name = str(excel_product_name).strip()

            # 1. 상품명 100% 일치 확인
            if order_product_name == excel_product_name:
                match_info = {
                    '탭': tab_name,
                    '상품명': excel_product_name,
                    '유사도': 100.0,
                    '입고가계': str(row.get('입고가계', '')),
                    '공급가(V+) 배송비 포함': str(row.get('공급가(V+) 배송비 포함', '')),
                    '운영사': str(row.get('운영사', '')),
                    '대표 1': str(row.get('대표 1', '')),
                    '모델명': str(row.get('모델명', '')) if model_col else ''
                }
                return match_info, "100%일치"

            # 2. 모델명 100% 포함 확인
            if model_col:
                model_name = row.get(model_col, '')
                if not pd.isna(model_name) and str(model_name).strip():
                    normalized_model = normalize_string(str(model_name).strip())

                    # 정규화된 모델명이 정규화된 시트 상품명에 100% 포함되는지 확인
                    if normalized_model and normalized_model in normalized_order:
                        match_info = {
                            '탭': tab_name,
                            '상품명': excel_product_name,
                            '유사도': 100.0,
                            '입고가계': str(row.get('입고가계', '')),
                            '공급가(V+) 배송비 포함': str(row.get('공급가(V+) 배송비 포함', '')),
                            '운영사': str(row.get('운영사', '')),
                            '대표 1': str(row.get('대표 1', '')),
                            '모델명': str(model_name)
                        }
                        return match_info, "모델명100%일치"

    return None, None
