"""
엑셀 파일 전처리 모듈
- 이미지 제거
- 파일 최적화
"""
import zipfile
from pathlib import Path


def remove_images_from_xlsx(src_path, dst_path, remove_drawings=True):
    """
    엑셀(.xlsx, .xlsm) 내부 이미지 파일 제거 후 새 파일로 저장.

    Args:
        src_path: 원본 엑셀 파일 경로 (Path 또는 str)
        dst_path: 결과 엑셀 파일 경로 (Path 또는 str)
        remove_drawings: True면 drawing(도형/차트 이미지 연결부)도 같이 제거

    Returns:
        bool: 성공 여부
    """
    src = Path(src_path)
    dst = Path(dst_path)

    if not src.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {src}")

    if src.suffix.lower() not in [".xlsx", ".xlsm"]:
        raise ValueError("이 스크립트는 .xlsx / .xlsm 형식만 지원합니다.")

    try:
        with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                name = item.filename

                # 1) 실제 이미지 파일들
                if name.startswith("xl/media/"):
                    continue

                # 2) drawing (이미지/도형/차트 연결부)
                if remove_drawings and name.startswith("xl/drawings/"):
                    continue

                data = zin.read(name)
                zout.writestr(item, data)

        return True
    except Exception as e:
        raise Exception(f"이미지 제거 중 오류: {str(e)}")
