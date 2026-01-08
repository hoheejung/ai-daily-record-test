# AI Project Context: 햇살 어린이집 AI 알림장

## 1. 프로젝트 개요
- **목표:** 어린이집 선생님들이 사진과 키워드 입력만으로 학부모에게 보낼 알림장을 자동 생성하는 서비스.
- **현재 상태:** Streamlit 기반 프로토타입 개발 및 GitHub 배포 완료.
- **향후 계획:** Next.js + Supabase 기반의 상용 서비스로 전환 (구독 모델, 성장 일기 기능).

## 2. 기술 스택 (Current Prototype)
- **Frontend/Backend:** Streamlit (Python)
- **AI Model:** Google Gemini 2.5 Flash
- **Image Processing:** Pillow (다중 이미지 리사이징 및 처리)
- **Deployment:** GitHub -> Streamlit Community Cloud
- **Security:** 
  - `.env` 및 Streamlit Secrets로 API Key 관리
  - 로컬 캐시(`st.cache_resource`)를 활용한 하루 생성 횟수 제한 (현재 300회)

## 3. 주요 기능 (Implemented)
- **멀티모달 생성:** 사진(여러 장) + 키워드 -> 감성적인 알림장 텍스트 생성.
- **복사 편의성:** 생성된 텍스트 우측 상단 복사 버튼 제공 (`st.code` 활용).
- **Few-shot Learning (말투 학습):** 
  - 사용자가 사이드바에 평소 말투 예시를 직접 입력.
  - `data/style_reference.txt`에 로컬 저장하여 반영구적 사용.
  - AI 프롬프트에 해당 말투를 포함하여 스타일 모방.
- **보안/제한:** 
  - 접속 코드(비밀번호) 기능은 삭제됨 (접근성 향상).
  - 하루 300회 생성 제한 (비용 방지).

## 4. 파일 구조
- `app.py`: 메인 애플리케이션 로직.
- `requirements.txt`: 의존성 패키지 목록.
- `.env`: (Git 제외) API Key 등 민감 정보.
- `data/`: (Git 제외) `style_reference.txt` 등 로컬 데이터 저장소.
- `GEMINI.md`: AI 에이전트 컨텍스트 파일.

## 5. 로드맵 (Migration to Next.js)
1. **Tech Stack:** Next.js (App Router), Supabase (Auth, DB, Storage), Vercel.
2. **Database Schema (Proposed):**
   - `users`: 선생님 계정 정보.
   - `students`: 반 아이들 정보.
   - `posts`: 알림장 기록 (content, generated_at).
   - `photos`: 스토리지 URL 연결.
3. **Features to Add:**
   - 회원가입/로그인 (Auth).
   - 결제 연동 (Subscription).
   - 성장 앨범 (Timeline) 및 PDF 출력.
   - 이미지 저장소 최적화 (Cloudflare R2 고려 - 대규모 트래픽 발생 시).
