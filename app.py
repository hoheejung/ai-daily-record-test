import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 상수 설정
STYLE_FILE_PATH = os.path.join("data", "style_reference.txt")

# 페이지 설정
st.set_page_config(page_title="햇살 어린이집 AI 알림장", page_icon="📝")

# Gemini API 설정
api_key = os.getenv("GOOGLE_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.sidebar.error("⚠️ .env 파일에 API 키를 설정해주세요.")

# --- 사이드바: 스타일 설정 ---
st.sidebar.header("🎨 나만의 말투 설정")

# 저장된 스타일 로드
saved_style_content = ""
if os.path.exists(STYLE_FILE_PATH):
    with open(STYLE_FILE_PATH, "r", encoding="utf-8") as f:
        saved_style_content = f.read()

# 접이식 메뉴 (기본값: 접힘)
with st.sidebar.expander("내 말투 예시 입력/수정", expanded=False):
    st.write("평소 쓰시는 알림장 문구들을 아래에 적어주세요. AI가 이 스타일을 학습합니다.")
    new_style_content = st.text_area(
        "말투 예시 (여러 문장을 적을수록 정확해요)", 
        value=saved_style_content, 
        height=300,
        placeholder="예: 오늘은 우리 아이들이 블록 놀이를 했어요! 듬직하게 앉아서..."
    )
    
    if st.button("💾 내 말투 저장하기"):
        if new_style_content.strip():
            with open(STYLE_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(new_style_content)
            st.success("말투가 저장되었습니다!")
            st.rerun()
        else:
            st.warning("내용을 입력해주세요.")

# 상태 표시 및 초기화
if saved_style_content:
    st.sidebar.write("🟢 **나만의 말투 적용 중**")
    if st.sidebar.button("🗑️ 말투 초기화"):
        if os.path.exists(STYLE_FILE_PATH):
            os.remove(STYLE_FILE_PATH)
        st.rerun()
else:
    st.sidebar.write("⚪ **기본 말투 적용 중**")

# --- 메인 UI ---
st.title("📝 우리 아이 AI 알림장")
st.subheader("사진과 키워드로 따뜻한 알림장을 만들어보세요.")

# 사진 업로드
uploaded_files = st.file_uploader("오늘의 활동 사진을 선택해주세요 (여러 장 가능)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

images = []
if uploaded_files:
    # 이미지를 보기 좋게 나열 (최대 3열)
    cols = st.columns(3)
    for idx, uploaded_file in enumerate(uploaded_files):
        image = Image.open(uploaded_file)
        images.append(image)
        with cols[idx % 3]:
            st.image(image, caption=f"사진 {idx+1}", use_container_width=True)

# 키워드 입력
keywords = st.text_input("아이의 활동 키워드를 입력해주세요 (예: 모래놀이, 웃음, 친구와 양보)")

# 생성 버튼
if st.button("✨ 알림장 생성"):
    if not api_key:
        st.error("먼저 API 키를 입력해주세요.")
    elif not uploaded_files:
        st.error("활동 사진을 최소 한 장 이상 업로드해주세요.")
    elif not keywords:
        st.error("키워드를 입력해주세요.")
    else:
        with st.spinner("선생님의 마음을 담아 알림장을 작성하고 있어요..."):
            try:
                # Gemini 2.5 Flash 모델 설정
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 스타일 파일 로드 확인
                style_instruction = ""
                if os.path.exists(STYLE_FILE_PATH):
                    with open(STYLE_FILE_PATH, "r", encoding="utf-8") as f:
                        user_style_text = f.read()
                    style_instruction = f"""
                    [참고할 선생님의 말투 예시]
                    아래 텍스트는 내가 평소에 쓰는 글 스타일이야. 이 톤앤매너, 문체, 이모티콘 사용법을 그대로 흉내내서 작성해줘:
                    ---
                    {user_style_text}
                    ---
                    """

                # 프롬프트 구성
                prompt = f"""
                당신은 아주 다정하고 세심한 어린이집 선생님입니다. 
                첨부된 {len(images)}장의 활동 사진들과 아래 제공된 키워드를 바탕으로 학부모님께 보낼 알림장을 작성해주세요.
                사진들의 내용을 종합해서 아이가 어떤 활동을 했는지 자연스럽게 연결해서 서술해주세요.
                
                {style_instruction}

                키워드: {keywords}
                
                [작성 지침]
                1. 말투는 매우 다정하고 따뜻하게 해주세요. ('~했어요', '~했답니다' 등)
                2. 아이의 활동을 구체적으로 칭찬하고 묘사해주세요.
                3. 부모님이 아이의 하루를 생생하게 느낄 수 있도록 감성적으로 작성해주세요.
                4. 한국어로 작성해주세요.
                """
                
                # API 호출 (프롬프트 + 이미지 리스트)
                # content 리스트에 프롬프트와 이미지 객체들을 모두 넣습니다.
                content = [prompt] + images
                response = model.generate_content(content)
                
                # 결과 출력
                st.success("따뜻한 알림장이 완성되었습니다!")
                
                # st.code는 우측 상단에 복사 버튼을 자동으로 제공합니다.
                # language="text"로 설정하여 코드 하이라이팅 없이 텍스트 그대로 보여줍니다.
                st.code(response.text, language="text", wrap_lines=True)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

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
