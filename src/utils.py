"""
유틸리티 함수 - 구글 시트 및 엑셀 처리
"""
import os
import glob
import gspread
from google.oauth2 import service_account
import pandas as pd


def get_service_account_file(search_dir=None):
    """
    config 폴더에서 Google API JSON 파일을 찾아 반환

    Args:
        search_dir: 검색할 디렉토리 (None이면 ../config)

    Returns:
        str: JSON 파일 경로 또는 None
    """
    if search_dir is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        search_dir = os.path.join(os.path.dirname(current_dir), "config")

    if not os.path.exists(search_dir):
        return None

    json_files = glob.glob(os.path.join(search_dir, "*.json"))

    if not json_files:
        return None

    # Google Sheets API.json 우선 선택
    for json_file in json_files:
        if "Sheets API" in json_file or "Sheet" in json_file:
            return json_file

    # 없으면 첫 번째 JSON 파일
    return json_files[0]


def get_gspread_client():
    """
    gspread 클라이언트 생성
    Streamlit Cloud에서는 secrets를 사용하고, 로컬에서는 JSON 파일 사용

    Returns:
        gspread.Client: 인증된 클라이언트
    """
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        # Streamlit Cloud secrets 시도
        import streamlit as st
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=SCOPES
            )
            return gspread.authorize(credentials)
    except:
        pass

    # 로컬 JSON 파일 사용
    json_path = get_service_account_file()
    if not json_path:
        raise FileNotFoundError("Google API JSON 파일을 찾을 수 없습니다. config 폴더에 'Google Sheets API.json' 파일을 추가하거나 Streamlit Secrets를 설정하세요.")

    credentials = service_account.Credentials.from_service_account_file(
        json_path, scopes=SCOPES
    )

    return gspread.authorize(credentials)


def load_matching_sheet_orders(client, sheet_name="상품매칭용시트"):
    """
    구글 스프레드시트에서 매칭 안 된 주문 데이터 읽기
    (매칭상품_상품명 컬럼이 비어있는 행만 반환)

    Args:
        client: gspread.Client
        sheet_name: 스프레드시트 이름

    Returns:
        pd.DataFrame: 주문 데이터 (상품명 컬럼 포함, 매칭 안 된 행만)
    """
    try:
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.worksheet("시트1")  # 시트1에서 읽기

        # 전체 데이터 가져오기
        data = worksheet.get_all_values()

        if not data:
            return pd.DataFrame()

        # 헤더와 데이터 분리
        headers = data[0]
        rows = data[1:]

        # DataFrame 생성
        df = pd.DataFrame(rows, columns=headers)

        # 필요한 컬럼만 선택 (상품명 필수)
        if "상품명" not in df.columns:
            raise ValueError("'상품명' 컬럼을 찾을 수 없습니다.")

        # 매칭상품_상품명 컬럼이 있으면 비어있는 행만 필터링
        if "매칭상품_상품명" in df.columns:
            # 매칭상품_상품명이 비어있거나 공백인 행만 선택
            df = df[df["매칭상품_상품명"].str.strip() == ""]

        return df

    except gspread.exceptions.SpreadsheetNotFound:
        raise FileNotFoundError(f"'{sheet_name}' 스프레드시트를 찾을 수 없습니다. 공유 설정을 확인하세요.")
    except Exception as e:
        raise Exception(f"스프레드시트 로드 오류: {str(e)}")


def load_excel_products(file_path, exclude_tabs=None):
    """
    엑셀 파일의 모든 탭에서 상품 데이터 로드

    Args:
        file_path: 엑셀 파일 경로
        exclude_tabs: 제외할 탭 리스트 (기본: ['월말재고현황'])

    Returns:
        dict: {탭명: DataFrame} 형태
    """
    if exclude_tabs is None:
        exclude_tabs = ['월말재고현황']

    excel_file = None
    try:
        # 엑셀 파일의 모든 시트 이름 가져오기
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names

        products = {}

        for sheet_name in sheet_names:
            # 제외할 탭은 건너뛰기
            if sheet_name in exclude_tabs:
                continue

            # 각 탭 읽기 (1행이 헤더)
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)

            # 빈 데이터프레임은 제외
            if not df.empty:
                products[sheet_name] = df

        return products

    except Exception as e:
        raise Exception(f"엑셀 파일 로드 오류: {str(e)}")
    finally:
        # 엑셀 파일 핸들 명시적으로 닫기
        if excel_file is not None:
            excel_file.close()


def update_matching_result(client, sheet_name, row_index, matched_data, match_type="수동매칭"):
    """
    매칭 결과를 시트1에 업데이트

    Args:
        client: gspread.Client
        sheet_name: 스프레드시트 이름
        row_index: 업데이트할 행 번호 (1-based)
        matched_data: 매칭된 데이터 딕셔너리
            - 상품명: str
            - 매입: str (입고가계)
            - 매출: str (공급가(V+) 배송비 포함)
            - 매입(업체): str (운영사)
            - 탭: str (엑셀 탭 이름)
            - 이미지URL: str (대표 1)
        match_type: 매칭 방식 ("100%일치", "모델명100%일치", "수동매칭")

    Returns:
        bool: 성공 여부
    """
    try:
        # batch_update_matching_results 함수를 재사용
        result = batch_update_matching_results(
            client,
            sheet_name,
            [{
                'row_index': row_index,
                'data': matched_data,
                'match_type': match_type
            }]
        )
        return result > 0

    except Exception as e:
        print(f"업데이트 오류: {str(e)}")
        return False


def get_matching_sheet_headers(client, sheet_name="상품매칭용시트"):
    """
    스프레드시트의 헤더 정보 가져오기

    Args:
        client: gspread.Client
        sheet_name: 스프레드시트 이름

    Returns:
        list: 헤더 리스트
    """
    try:
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.worksheet("시트1")

        # 첫 번째 행 (헤더) 가져오기
        headers = worksheet.row_values(1)
        return headers

    except Exception as e:
        print(f"헤더 가져오기 오류: {str(e)}")
        return []


def get_spreadsheet_url(client, sheet_name="상품매칭용시트"):
    """
    스프레드시트 URL 가져오기

    Args:
        client: gspread.Client
        sheet_name: 스프레드시트 이름

    Returns:
        str: 스프레드시트 URL 또는 None
    """
    try:
        spreadsheet = client.open(sheet_name)
        return spreadsheet.url

    except Exception as e:
        print(f"URL 가져오기 오류: {str(e)}")
        return None


def batch_update_matching_results(client, sheet_name, matched_results):
    """
    여러 매칭 결과를 시트1에 일괄 업데이트 (API 호출 최소화)

    Args:
        client: gspread.Client
        sheet_name: 스프레드시트 이름
        matched_results: 매칭 결과 리스트
            [
                {
                    'row_index': int (1-based),
                    'data': {...},  # matched_data
                    'match_type': str
                },
                ...
            ]

    Returns:
        int: 성공한 업데이트 개수
    """
    if not matched_results:
        return 0

    try:
        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.worksheet("시트1")

        # 헤더 확인 및 필요 시 추가
        headers = worksheet.row_values(1)

        # 매칭 컬럼 찾기 또는 추가
        matching_columns = {
            '매칭상품_상품명': None,
            '매칭_매입': None,
            '매칭_매출': None,
            '매칭_매입(업체)': None,
            '매칭_탭': None,
            '매칭방식': None
        }

        for col_name in matching_columns.keys():
            try:
                matching_columns[col_name] = headers.index(col_name) + 1  # 1-based
            except ValueError:
                # 컬럼이 없으면 추가
                matching_columns[col_name] = len(headers) + 1
                headers.append(col_name)

        # 헤더 업데이트 (새 컬럼이 추가된 경우)
        if len(headers) > len(worksheet.row_values(1)):
            worksheet.update(f'A1:{chr(64 + len(headers))}1', [headers])

        # 기존 데이터 한 번에 가져오기
        all_data = worksheet.get_all_values()
        existing_matched = set()

        for i, row in enumerate(all_data):
            if i > 0:  # 헤더 제외
                # 매칭상품_상품명 컬럼에 값이 있으면 이미 매칭됨
                matched_col_idx = matching_columns['매칭상품_상품명'] - 1
                if len(row) > matched_col_idx and row[matched_col_idx].strip():
                    existing_matched.add(i + 1)  # 1-based index

        # 일괄 업데이트 데이터 준비
        updates = []
        format_requests = []
        soldout_rows = []  # 품절 탭 행 추적
        success_count = 0

        for result in matched_results:
            row_idx = result['row_index']

            # 이미 매칭된 행은 건너뛰기
            if row_idx in existing_matched:
                continue

            data = result['data']
            match_type = result.get('match_type', '수동매칭')
            tab_name = data.get('탭', '')

            # 각 컬럼별로 업데이트
            col_idx = matching_columns['매칭상품_상품명']
            updates.append({
                'range': f'{chr(64 + col_idx)}{row_idx}',
                'values': [[data.get('상품명', '')]]
            })

            col_idx = matching_columns['매칭_매입']
            updates.append({
                'range': f'{chr(64 + col_idx)}{row_idx}',
                'values': [[data.get('매입', '')]]
            })

            col_idx = matching_columns['매칭_매출']
            updates.append({
                'range': f'{chr(64 + col_idx)}{row_idx}',
                'values': [[data.get('매출', '')]]
            })

            col_idx = matching_columns['매칭_매입(업체)']
            updates.append({
                'range': f'{chr(64 + col_idx)}{row_idx}',
                'values': [[data.get('매입(업체)', '')]]
            })

            col_idx = matching_columns['매칭_탭']
            updates.append({
                'range': f'{chr(64 + col_idx)}{row_idx}',
                'values': [[tab_name]]
            })

            col_idx = matching_columns['매칭방식']
            updates.append({
                'range': f'{chr(64 + col_idx)}{row_idx}',
                'values': [[match_type]]
            })

            # 품절 탭인 경우 서식 요청 추가
            if '품절' in tab_name:
                soldout_rows.append({
                    'row_idx': row_idx,
                    'tab_col_idx': matching_columns['매칭_탭']
                })

            success_count += 1

        # 일괄 업데이트 실행
        if updates:
            worksheet.batch_update(updates)

        # 품절 탭 서식 적용
        if soldout_rows:
            _apply_soldout_formatting(worksheet, soldout_rows, len(headers))

        return success_count

    except Exception as e:
        print(f"일괄 업데이트 오류: {str(e)}")
        return 0


def _apply_soldout_formatting(worksheet, soldout_rows, total_columns):
    """
    품절 탭 행에 서식 적용
    - 전체 행: 연한 빨간색 배경 (#ffcccc)
    - 매칭_탭 셀: 강한 빨간색 배경 (#ff0000) + 흰색 텍스트
    """
    try:
        requests = []

        for row_info in soldout_rows:
            row_idx = row_info['row_idx'] - 1  # 0-based index
            tab_col_idx = row_info['tab_col_idx'] - 1  # 0-based index

            # 전체 행 배경색 (연한 빨간색)
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': worksheet.id,
                        'startRowIndex': row_idx,
                        'endRowIndex': row_idx + 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': total_columns
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': 1.0,
                                'green': 0.8,
                                'blue': 0.8
                            }
                        }
                    },
                    'fields': 'userEnteredFormat.backgroundColor'
                }
            })

            # 매칭_탭 셀 강조 (강한 빨간색 + 흰색 텍스트)
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': worksheet.id,
                        'startRowIndex': row_idx,
                        'endRowIndex': row_idx + 1,
                        'startColumnIndex': tab_col_idx,
                        'endColumnIndex': tab_col_idx + 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': 1.0,
                                'green': 0.0,
                                'blue': 0.0
                            },
                            'textFormat': {
                                'foregroundColor': {
                                    'red': 1.0,
                                    'green': 1.0,
                                    'blue': 1.0
                                },
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })

        # 서식 적용
        if requests:
            worksheet.spreadsheet.batch_update({'requests': requests})

    except Exception as e:
        print(f"서식 적용 오류: {str(e)}")
