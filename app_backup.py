import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import datetime

# 환경 변수 로드
load_dotenv()

# 상수 설정
STYLE_FILE_PATH = os.path.join("data", "style_reference.txt")
DAILY_LIMIT = 100  # 하루 최대 생성 횟수 제한

# 페이지 설정
st.set_page_config(page_title="우리선생님 문서도우미", page_icon="☀️")

# --- 세션 상태 초기화
if "daily_result" not in st.session_state:
    st.session_state.daily_result = None
if "notice_result" not in st.session_state:
    st.session_state.notice_result = None

# --- 안전장치: 하루 사용량 제한 ---
@st.cache_resource
def get_usage_counter():
    return {"date": datetime.date.today(), "count": 0}

usage_data = get_usage_counter()
if usage_data["date"] != datetime.date.today():
    usage_data["date"] = datetime.date.today()
    usage_data["count"] = 0

# --- Gemini API 설정 ---
api_key = os.getenv("GOOGLE_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# ==========================================
# [사이드바 구성]
# ==========================================
st.sidebar.title("우리선생님 문서도우미")

# 메뉴 선택
menu = st.sidebar.radio("메뉴 선택", ["📝 알림장 (개인)", "📢 공지사항 (전체)"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"📊 **오늘 생성 횟수:** {usage_data['count']} / {DAILY_LIMIT}")

if not api_key:
    st.sidebar.error("⚠️ .env 파일에 API 키를 설정해주세요.")

# ==========================================
# [메인 화면 구성]
# ==========================================

# --- 1. 알림장 (개인) ---
if menu == "📝 알림장 (개인)":
    st.title("📝 우리 아이 알림장")
    st.subheader("사진과 키워드로 따뜻한 알림장을 작성합니다.")

    # --- 말투 설정 ---
    with st.expander("🎨 나만의 말투 설정 (클릭해서 열기)", expanded=False):
        st.info("평소 쓰시는 알림장 문구를 적어주시면 AI가 선생님의 말투를 따라합니다.")
        
        saved_style_content = ""
        if os.path.exists(STYLE_FILE_PATH):
            with open(STYLE_FILE_PATH, "r", encoding="utf-8") as f:
                saved_style_content = f.read()
        
        new_style_content = st.text_area(
            "말투 예시 입력", 
            value=saved_style_content, 
            height=150,
            placeholder="예: 오늘은 우리 아이들이 블록 놀이를 했어요! 듬직하게 앉아서..."
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾 말투 저장하기"):
                if new_style_content.strip():
                    with open(STYLE_FILE_PATH, "w", encoding="utf-8") as f:
                        f.write(new_style_content)
                    st.success("말투가 저장되었습니다!")
                    st.rerun()
        with col2:
            if saved_style_content:
                if st.button("🗑️ 말투 초기화"):
                    if os.path.exists(STYLE_FILE_PATH):
                        os.remove(STYLE_FILE_PATH)
                    st.rerun()

    if saved_style_content:
        st.success(f"🟢 현재 **나만의 말투**가 적용되어 있습니다.")
    
    st.markdown("---")

    # --- 사진 및 키워드 입력 ---
    uploaded_files = st.file_uploader("활동 사진 (여러 장 가능)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    if uploaded_files:
        cols = st.columns(min(3, len(uploaded_files)))
        for idx, uploaded_file in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(uploaded_file, caption=f"사진 {idx+1}", use_container_width=True)

    keywords = st.text_input("활동 키워드 (예: 모래놀이, 웃음)", key="input_daily")

    # --- 버튼 및 이모티콘 토글 ---
    col_btn, col_toggle = st.columns([3, 1])
    use_emoji = col_toggle.toggle("이모티콘 사용", value=True, key="emoji_daily_toggle")
    
    if col_btn.button("✨ 알림장 생성", key="daily_btn"):
        if not api_key or not uploaded_files or not keywords:
            st.error("API 키, 사진, 키워드를 모두 확인해주세요.")
        elif usage_data["count"] >= DAILY_LIMIT:
            st.error("오늘의 한도를 초과했습니다.")
        else:
            with st.spinner("알림장을 작성하고 있어요..."):
                try:
                    images = [Image.open(f) for f in uploaded_files]
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    current_style = saved_style_content if saved_style_content else ""
                    style_instruction = f"말투 예시:\n{current_style}" if current_style else ""
                    
                    # 이모티콘 지침 동적 적용
                    emoji_instruction = "문장 사이사이에 내용과 어울리는 이모티콘(😊, 🌳, 🎈 등)을 풍부하게 사용해줘." if use_emoji else "이모티콘을 절대 사용하지 말고 텍스트로만 정중하게 작성해줘."
                    
                    prompt = f"""
                    당신은 다정한 어린이집 선생님입니다. 사진과 키워드를 보고 학부모님께 보낼 알림장을 작성해주세요.
                    키워드: {keywords}
                    {style_instruction}
                    [지침]
                    1. 아주 다정하고 따뜻한 말투 ('~했어요', '~했답니다')
                    2. 아이의 활동을 구체적으로 칭찬
                    3. {emoji_instruction}
                    4. 한국어로 작성
                    """
                    response = model.generate_content([prompt] + images)
                    st.session_state.daily_result = response.text
                    usage_data["count"] += 1
                except Exception as e:
                    st.error(f"오류: {e}")

    # 결과 표시
    if st.session_state.daily_result:
        st.divider()
        st.success("따뜻한 알림장이 완성되었습니다!")
        st.code(st.session_state.daily_result, language="text", wrap_lines=True)

# --- 2. 공지사항 (전체) ---
elif menu == "📢 공지사항 (전체)":
    st.title("📢 학부모님 전체 공지사항")
    st.subheader("중요한 내용을 정중하고 따뜻하게 전달합니다.")

    notice_keywords = st.text_area("공지 내용 (예: 이번 주 금요일 생일파티, 10시 시작, 준비물 없음)", height=150, key="input_notice")
    
    # --- 버튼 및 이모티콘 토글 ---
    col_btn, col_toggle = st.columns([3, 1])
    use_emoji_notice = col_toggle.toggle("이모티콘 사용", value=True, key="emoji_notice_toggle")
    
    if col_btn.button("✨ 공지사항 생성", key="notice_btn"):
        if not api_key or not notice_keywords:
            st.error("내용을 입력해주세요.")
        elif usage_data["count"] >= DAILY_LIMIT:
            st.error("오늘의 한도를 초과했습니다.")
        else:
            with st.spinner("공지사항을 다듬고 있어요..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # 이모티콘 지침 동적 적용
                    emoji_instruction = "적절한 위치에 이모티콘을 사용하여 따뜻하게 표현해줘." if use_emoji_notice else "이모티콘을 전혀 사용하지 말고 명확하고 정중하게 텍스트로만 작성해줘."
                    
                    prompt = f"""
                    당신은 베테랑 어린이집 선생님입니다. 학부모님 전체에게 보낼 공지사항을 작성해주세요.
                    내용: {notice_keywords}
                    [지침]
                    1. 정중하면서도 따뜻한 어조
                    2. 제목(예: [공지])을 포함할 것
                    3. 날짜, 시간 등 중요 정보는 명확하게
                    4. {emoji_instruction}
                    5. 한국어로 작성
                    """
                    response = model.generate_content(prompt)
                    st.session_state.notice_result = response.text
                    usage_data["count"] += 1
                except Exception as e:
                    st.error(f"오류: {e}")

    # 결과 표시
    if st.session_state.notice_result:
        st.divider()
        st.success("공지사항이 작성되었습니다!")
        st.code(st.session_state.notice_result, language="text", wrap_lines=True)

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #FFB347;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
