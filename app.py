import streamlit as st
from PIL import Image
from dotenv import load_dotenv

# 분리한 모듈 임포트
import config
import utils
import services

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(page_title=config.PAGE_TITLE, page_icon=config.PAGE_ICON)

# --- 세션 상태 초기화 ---
if "daily_result" not in st.session_state:
    st.session_state.daily_result = None
if "notice_result" not in st.session_state:
    st.session_state.notice_result = None

# --- 사용량 제한 체크 ---
usage_data = utils.get_usage_counter()
utils.check_and_reset_usage(usage_data)

# --- Gemini API 설정 ---
api_key = services.configure_genai()

# ==========================================
# [사이드바 구성]
# ==========================================
st.sidebar.title(f"{config.PAGE_ICON} {config.PAGE_TITLE}")

# 메뉴 선택
menu = st.sidebar.radio("메뉴 선택", ["📝 알림장 (개인)", "📢 공지사항 (전체)"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"📊 **오늘 생성 횟수:** {usage_data['count']} / {config.DAILY_LIMIT}")

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
        
        saved_style_content = utils.load_style()
        
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
                    if utils.save_style(new_style_content):
                        st.success("말투가 저장되었습니다!")
                        st.rerun()
        with col2:
            if saved_style_content:
                if st.button("🗑️ 말투 초기화"):
                    if utils.remove_style():
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
        if not api_key:
             st.error("API 키가 설정되지 않았습니다.")
        elif not uploaded_files or not keywords:
            st.error("사진과 키워드를 모두 입력해주세요.")
        elif usage_data["count"] >= config.DAILY_LIMIT:
            st.error("오늘의 생성 한도를 초과했습니다.")
        else:
            with st.spinner("알림장을 작성하고 있어요..."):
                try:
                    # PIL 이미지 객체로 변환
                    images = [Image.open(f) for f in uploaded_files]
                    
                    result_text = services.generate_daily_notice(
                        images=images,
                        keywords=keywords,
                        style_content=saved_style_content,
                        use_emoji=use_emoji
                    )
                    
                    st.session_state.daily_result = result_text
                    usage_data["count"] += 1
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

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
        if not api_key:
             st.error("API 키가 설정되지 않았습니다.")
        elif not notice_keywords:
            st.error("공지 내용을 입력해주세요.")
        elif usage_data["count"] >= config.DAILY_LIMIT:
            st.error("오늘의 생성 한도를 초과했습니다.")
        else:
            with st.spinner("공지사항을 다듬고 있어요..."):
                try:
                    result_text = services.generate_public_notice(
                        notice_keywords=notice_keywords,
                        use_emoji=use_emoji_notice
                    )
                    
                    st.session_state.notice_result = result_text
                    usage_data["count"] += 1
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

    # 결과 표시
    if st.session_state.notice_result:
        st.divider()
        st.success("공지사항이 작성되었습니다!")
        st.code(st.session_state.notice_result, language="text", wrap_lines=True)

# CSS 스타일링 (버튼 등)
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