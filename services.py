import google.generativeai as genai
import os
from PIL import Image
from typing import List, Optional
from config import MODEL_NAME, PROMPT_DAILY_NOTICE, PROMPT_PUBLIC_NOTICE, EMOJI_INSTRUCTION_ON, EMOJI_INSTRUCTION_OFF

def configure_genai() -> str:
    """환경 변수에서 API 키를 로드하고 Gemini를 설정합니다."""
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
    return api_key

def get_emoji_instruction(use_emoji: bool) -> str:
    """이모티콘 사용 여부에 따른 지침 텍스트를 반환합니다."""
    return EMOJI_INSTRUCTION_ON if use_emoji else EMOJI_INSTRUCTION_OFF

def generate_daily_notice(
    images: List[Image.Image], 
    keywords: str, 
    style_content: str, 
    use_emoji: bool
) -> Optional[str]:
    """알림장(개인)을 생성합니다."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        style_instruction = f"말투 예시:\n{style_content}" if style_content else ""
        emoji_instruction = get_emoji_instruction(use_emoji)
        
        prompt = PROMPT_DAILY_NOTICE.format(
            keywords=keywords,
            style_instruction=style_instruction,
            emoji_instruction=emoji_instruction
        )
        
        # 텍스트 프롬프트와 이미지 리스트를 함께 전달
        response = model.generate_content([prompt] + images)
        return response.text
    except Exception as e:
        # 실제 운영시에는 로깅을 하는 것이 좋음
        raise e

def generate_public_notice(
    notice_keywords: str, 
    use_emoji: bool
) -> Optional[str]:
    """공지사항(전체)을 생성합니다."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        emoji_instruction = get_emoji_instruction(use_emoji)
        
        prompt = PROMPT_PUBLIC_NOTICE.format(
            notice_keywords=notice_keywords,
            emoji_instruction=emoji_instruction
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise e
