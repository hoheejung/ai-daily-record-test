import os

# --- 설정 상수 ---
DAILY_LIMIT = 100
STYLE_FILE_PATH = os.path.join("data", "style_reference.txt")
PAGE_TITLE = "우리선생님 AI"
PAGE_ICON = "☀️"
MODEL_NAME = 'gemini-2.5-flash'

# --- 프롬프트 템플릿 ---
# 1. 알림장 (개인)
PROMPT_DAILY_NOTICE = """
당신은 다정한 어린이집 선생님입니다. 사진과 키워드를 보고 학부모님께 보낼 알림장을 작성해주세요.
키워드: {keywords}
{style_instruction}

[지침]
1. 아주 다정하고 따뜻한 말투 ('~했어요', '~했답니다')
2. 아이의 활동을 구체적으로 칭찬
3. {emoji_instruction}
4. 한국어로 작성
"""

# 2. 공지사항 (전체)
PROMPT_PUBLIC_NOTICE = """
당신은 베테랑 어린이집 선생님입니다. 학부모님 전체에게 보낼 공지사항을 작성해주세요.
내용: {notice_keywords}

[지침]
1. 정중하면서도 따뜻한 어조
2. 제목(예: [공지])을 포함할 것
3. 날짜, 시간 등 중요 정보는 명확하게
4. {emoji_instruction}
5. 한국어로 작성
"""

# 이모티콘 지침
EMOJI_INSTRUCTION_ON = "문장 사이사이에 내용과 어울리는 이모티콘(😊, 🌳, 🎈 등)을 풍부하게 사용해줘."
EMOJI_INSTRUCTION_OFF = "이모티콘을 절대 사용하지 말고 텍스트로만 정중하게 작성해줘."
