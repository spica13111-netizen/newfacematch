"""
이미지 다운로드 및 처리 모듈
"""
import io
import requests
from PIL import Image
import base64


def download_and_resize_image(image_url, size=(100, 100), timeout=10):
    """
    URL에서 이미지 다운로드 후 리사이즈

    Args:
        image_url: 이미지 URL
        size: 리사이즈할 크기 (width, height)
        timeout: 다운로드 타임아웃 (초)

    Returns:
        bytes: 리사이즈된 이미지 바이트 또는 None
    """
    if not image_url or not str(image_url).startswith('http'):
        return None

    try:
        # 이미지 다운로드
        response = requests.get(image_url, timeout=timeout, stream=True)
        response.raise_for_status()

        # PIL Image로 변환
        image = Image.open(io.BytesIO(response.content))

        # RGBA 모드면 RGB로 변환 (JPEG 저장을 위해)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')

        # 비율 유지하며 리사이즈
        image.thumbnail(size, Image.Resampling.LANCZOS)

        # 바이트로 변환
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85)
        output.seek(0)

        return output.getvalue()

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 오류 ({image_url}): {str(e)}")
        return None
    except Exception as e:
        print(f"이미지 처리 오류 ({image_url}): {str(e)}")
        return None


def get_image_base64(image_bytes):
    """
    이미지 바이트를 Base64로 인코딩

    Args:
        image_bytes: 이미지 바이트

    Returns:
        str: Base64 인코딩된 문자열
    """
    if not image_bytes:
        return None

    return base64.b64encode(image_bytes).decode('utf-8')


def insert_image_to_sheet(worksheet, cell_range, image_url, size=(100, 100)):
    """
    구글 시트에 이미지 삽입

    Args:
        worksheet: gspread.Worksheet 객체
        cell_range: 이미지를 삽입할 셀 (예: 'F2')
        image_url: 이미지 URL
        size: 이미지 크기

    Returns:
        bool: 성공 여부
    """
    try:
        # 이미지 다운로드 및 리사이즈
        image_bytes = download_and_resize_image(image_url, size)

        if not image_bytes:
            return False

        # gspread에서 이미지 삽입은 복잡하므로
        # 일단 이미지 URL만 텍스트로 저장
        # (실제 이미지 삽입은 Google Sheets API의 batchUpdate 필요)
        worksheet.update(cell_range, f"=IMAGE(\"{image_url}\", 1)")

        return True

    except Exception as e:
        print(f"이미지 삽입 오류: {str(e)}")
        return False


def validate_image_url(image_url):
    """
    이미지 URL이 유효한지 확인

    Args:
        image_url: 확인할 URL

    Returns:
        bool: 유효 여부
    """
    if not image_url or not isinstance(image_url, str):
        return False

    if not image_url.startswith('http'):
        return False

    # 이미지 확장자 확인 (선택적)
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    lower_url = image_url.lower()

    # URL에 확장자가 있으면 검증, 없으면 통과
    if any(ext in lower_url for ext in valid_extensions):
        return True

    # 확장자가 명확하지 않은 경우도 일단 시도
    return True
