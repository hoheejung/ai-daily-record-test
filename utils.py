import os
import datetime
import streamlit as st
from config import STYLE_FILE_PATH

def load_style() -> str:
    """저장된 말투 스타일을 파일에서 읽어옵니다."""
    if os.path.exists(STYLE_FILE_PATH):
        try:
            with open(STYLE_FILE_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            st.error(f"말투 파일 로드 실패: {e}")
    return ""

def save_style(content: str) -> bool:
    """말투 스타일을 파일에 저장합니다."""
    try:
        # data 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(STYLE_FILE_PATH), exist_ok=True)
        with open(STYLE_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        st.error(f"말투 저장 실패: {e}")
        return False

def remove_style() -> bool:
    """저장된 말투 스타일 파일을 삭제합니다."""
    if os.path.exists(STYLE_FILE_PATH):
        try:
            os.remove(STYLE_FILE_PATH)
            return True
        except Exception as e:
            st.error(f"말투 삭제 실패: {e}")
            return False
    return False

# --- 사용량 제한 (Streamlit Cache 활용) ---
@st.cache_resource
def get_usage_counter():
    """하루 사용량을 추적하는 카운터 객체를 반환합니다 (세션 간 공유)."""
    return {"date": datetime.date.today(), "count": 0}

def check_and_reset_usage(usage_data):
    """날짜가 바뀌었는지 확인하고 카운터를 초기화합니다."""
    if usage_data["date"] != datetime.date.today():
        usage_data["date"] = datetime.date.today()
        usage_data["count"] = 0
