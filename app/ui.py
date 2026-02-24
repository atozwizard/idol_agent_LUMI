"""
Gradio 기반 채팅 인터페이스

FastAPI에 마운트되어 /ui 경로에서 서비스됩니다.

접속:
    - 로컬: http://localhost:8000/ui
"""

import gradio as gr
import httpx
import uuid
from loguru import logger


# ✨ 커스텀 CSS - 버추얼 아이돌 채팅앱 테마
CUSTOM_CSS = """
/* ===== Gradio Footer 숨김 ===== */
footer { display: none !important; }

/* ===== 폰트 임포트 ===== */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Quicksand:wght@400;500;600;700&display=swap');

/* ===== 전역 변수 ===== */
:root {
    --lumi-pink: #ff6b9d;
    --lumi-purple: #c44eff;
    --lumi-blue: #4ecaff;
    --lumi-gradient: linear-gradient(135deg, #ff6b9d 0%, #c44eff 50%, #4ecaff 100%);
    --glass-bg: rgba(255, 255, 255, 0.15);
    --glass-border: rgba(255, 255, 255, 0.3);
    --chat-user: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --chat-lumi: linear-gradient(135deg, #ff6b9d 0%, #ff8a80 100%);
}

/* ===== 메인 컨테이너 ===== */
.gradio-container {
    font-family: 'Noto Sans KR', 'Quicksand', sans-serif !important;
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #0f0c29) !important;
    background-size: 400% 400% !important;
    animation: gradientShift 15s ease infinite !important;
    min-height: 100vh !important;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ===== 오로라 오버레이 효과 ===== */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
        radial-gradient(ellipse at 20% 20%, rgba(255, 107, 157, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(196, 78, 255, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 40% 80%, rgba(78, 202, 255, 0.1) 0%, transparent 40%);
    pointer-events: none;
    z-index: 0;
}

/* ===== 반짝이는 별 효과 ===== */
.gradio-container::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image:
        radial-gradient(2px 2px at 20px 30px, rgba(255, 255, 255, 0.8), transparent),
        radial-gradient(2px 2px at 40px 70px, rgba(255, 107, 157, 0.6), transparent),
        radial-gradient(1px 1px at 90px 40px, rgba(196, 78, 255, 0.8), transparent),
        radial-gradient(2px 2px at 130px 80px, rgba(78, 202, 255, 0.6), transparent),
        radial-gradient(1px 1px at 160px 120px, white, transparent);
    background-repeat: repeat;
    background-size: 200px 200px;
    animation: twinkle 4s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
}

@keyframes twinkle {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.7; }
}

/* ===== 메인 콘텐츠 영역 ===== */
.main, .contain {
    position: relative;
    z-index: 1;
}

/* ===== 헤더 스타일 ===== */
.header-container {
    text-align: center;
    padding: 2rem 1rem;
    margin-bottom: 1rem;
}

.header-container h1 {
    font-family: 'Quicksand', sans-serif !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    background: var(--lumi-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 0 40px rgba(255, 107, 157, 0.5);
    margin-bottom: 0.5rem;
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from { filter: drop-shadow(0 0 20px rgba(255, 107, 157, 0.4)); }
    to { filter: drop-shadow(0 0 30px rgba(196, 78, 255, 0.6)); }
}

.header-container p {
    color: rgba(255, 255, 255, 0.8) !important;
    font-size: 1rem;
    font-weight: 300;
}

/* ===== 기능 태그 스타일 ===== */
.feature-tags {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1rem;
}

.feature-tag {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
    color: white;
    transition: all 0.3s ease;
}

.feature-tag:hover {
    background: rgba(255, 107, 157, 0.3);
    transform: translateY(-2px);
}

/* ===== 채팅 컨테이너 (글래스모피즘) ===== */
.chat-container {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 24px !important;
    box-shadow:
        0 8px 32px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    overflow: hidden;
}

/* ===== 채팅창 스타일 ===== */
.chatbot {
    background: transparent !important;
    border: none !important;
}

.chatbot .messages {
    background: transparent !important;
    padding: 1.5rem !important;
}

/* ===== 메시지 말풍선 (Gradio 6.0) ===== */
.chatbot .message-row {
    padding: 0.5rem 0 !important;
}

.chatbot .message-bubble {
    max-width: 80% !important;
    padding: 1rem 1.25rem !important;
    border-radius: 20px !important;
    line-height: 1.6 !important;
}

/* 사용자 메시지 */
.chatbot .message-row.user-row .message-bubble {
    background: var(--chat-user) !important;
    color: white !important;
    border-radius: 20px 20px 4px 20px !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

/* 루미(어시스턴트) 메시지 */
.chatbot .message-row.bot-row .message-bubble {
    background: linear-gradient(135deg, rgba(255, 107, 157, 0.3) 0%, rgba(196, 78, 255, 0.3) 100%) !important;
    border: 1px solid rgba(255, 107, 157, 0.4) !important;
    color: white !important;
    border-radius: 20px 20px 20px 4px !important;
    box-shadow: 0 4px 15px rgba(255, 107, 157, 0.2) !important;
    backdrop-filter: blur(10px) !important;
}

/* 메시지 텍스트 색상 강제 적용 */
.chatbot .message-bubble p,
.chatbot .message-bubble span,
.chatbot .message-bubble {
    color: white !important;
}

/* 아바타 스타일 */
.chatbot .avatar-container,
.chatbot .avatar-image {
    width: 40px !important;
    height: 40px !important;
    border-radius: 50% !important;
    overflow: hidden !important;
    border: 2px solid var(--glass-border) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

.chatbot .bot-row .avatar-container {
    background: var(--lumi-gradient) !important;
    border-color: rgba(255, 107, 157, 0.5) !important;
}

/* ===== 입력 영역 ===== */
.input-row {
    padding: 1rem 1.5rem 1.5rem !important;
    background: rgba(0, 0, 0, 0.2) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* 텍스트박스 - 모든 Gradio 입력창 타겟 */
.input-row textarea,
.input-row input[type="text"],
textarea,
input[type="text"],
.textbox textarea {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(255, 107, 157, 0.4) !important;
    border-radius: 16px !important;
    color: #1a1a1a !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 1rem !important;
    padding: 1rem 1.25rem !important;
    transition: all 0.3s ease !important;
    caret-color: var(--lumi-pink) !important;
}

.input-row textarea:focus,
.input-row input[type="text"]:focus,
textarea:focus,
input[type="text"]:focus,
.textbox textarea:focus {
    outline: none !important;
    border-color: var(--lumi-pink) !important;
    box-shadow: 0 0 20px rgba(255, 107, 157, 0.3) !important;
    background: #ffffff !important;
    color: #1a1a1a !important;
}

.input-row textarea::placeholder,
.input-row input[type="text"]::placeholder,
textarea::placeholder,
.textbox textarea::placeholder {
    color: rgba(150, 100, 120, 0.7) !important;
}

/* 전송 버튼 */
.send-btn {
    background: var(--lumi-gradient) !important;
    border: none !important;
    border-radius: 14px !important;
    color: white !important;
    font-weight: 600 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    padding: 0.8rem 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(255, 107, 157, 0.4) !important;
    text-transform: none !important;
}

.send-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(255, 107, 157, 0.5) !important;
}

.send-btn:active {
    transform: translateY(0) !important;
}

/* ===== 빠른 응답 버튼 ===== */
.quick-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    padding: 1rem;
}

.quick-btn {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 20px !important;
    color: white !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

.quick-btn:hover {
    background: rgba(255, 107, 157, 0.3) !important;
    border-color: rgba(255, 107, 157, 0.5) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3) !important;
}

/* ===== 초기화 버튼 ===== */
.clear-btn {
    background: transparent !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 12px !important;
    color: rgba(255, 255, 255, 0.7) !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.3s ease !important;
    margin-top: 0.5rem !important;
}

.clear-btn:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(255, 255, 255, 0.5) !important;
    color: white !important;
}

/* ===== 푸터 ===== */
.footer {
    text-align: center;
    padding: 1.5rem;
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.8rem;
}

.footer code {
    background: rgba(255, 255, 255, 0.1);
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.75rem;
}

/* ===== 섹션 라벨 숨기기 ===== */
.chatbot > label,
.block > label span {
    display: none !important;
}

/* ===== 스크롤바 스타일 ===== */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 107, 157, 0.3);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 107, 157, 0.5);
}

/* ===== 복사 버튼 숨기기 ===== */
.chatbot button[aria-label="Copy"],
.chatbot .copy-btn,
.chatbot .message-buttons,
.chatbot [data-testid="copy-btn"],
.chatbot svg.copy-icon,
button.copy {
    display: none !important;
}

/* ===== Processing 텍스트 숨기기 ===== */
.chatbot .pending,
.chatbot .generating,
.chatbot [data-testid="bot"][class*="pending"],
.message.pending .message-content::after {
    content: none !important;
}

/* processing... 텍스트 색상 (숨길 수 없으면 투명하게) */
.chatbot .bot.pending .message-bubble,
.chatbot .generating {
    color: transparent !important;
    background: rgba(255, 107, 157, 0.1) !important;
}

/* ===== 반응형 ===== */
@media (max-width: 768px) {
    .header-container h1 {
        font-size: 1.8rem !important;
    }

    .chatbot .user .message-content,
    .chatbot .bot .message-content {
        max-width: 85% !important;
    }

    .feature-tags {
        gap: 0.3rem;
    }

    .feature-tag {
        font-size: 0.75rem;
        padding: 0.3rem 0.7rem;
    }
}
"""

# 테마 설정
THEME = gr.themes.Base(
    primary_hue="pink",
    secondary_hue="purple",
    neutral_hue="slate",
)


def create_chat_handler():
    """
    채팅 핸들러 생성 (Direct Call 방식)
    """
    from app.api.routes.chat import chat
    from app.schemas.chat import ChatRequest

    async def chat_with_lumi(message: str, history: list, session_id: str) -> str:
        """
        루미와 대화합니다. (Direct Call)

        HTTP 요청 대신 내부 컨트롤러를 직접 호출하여
        네트워크(localhost/port) 문제 없이 동작합니다.

        Args:
            message: 사용자 메시지
            history: 대화 히스토리
            session_id: 사용자별 고유 세션 ID (gr.State로 관리)
        """
        if not message.strip():
            return "메시지를 입력해주세요!"

        try:
            # 1. 요청 객체 생성
            request = ChatRequest(
                message=message,
                session_id=session_id
            )

            # 2. 컨트롤러 직접 호출 (await)
            response = await chat(request)

            # 3. 응답 처리
            ai_message = response.message
            
            # Tool 사용 여부 표시
            if response.tool_used:
                ai_message += f"\n\n✨ _{response.tool_used}_"

            return ai_message

        except Exception as e:
            logger.error(f"채팅 오류: {e}")
            return f"앗, 오류가 발생했어요: {str(e)}"

    return chat_with_lumi


def create_demo() -> gr.Blocks:
    """
    Gradio 데모 앱 생성

    Returns:
        gr.Blocks: Gradio 앱
    """
    chat_with_lumi = create_chat_handler()

    # 🔧 세션 ID 생성 헬퍼 함수
    def generate_session_id() -> str:
        """브라우저 탭마다 고유한 세션 ID 생성"""
        new_id = f"gradio-{uuid.uuid4().hex[:8]}"
        logger.info(f"🔑 새 Gradio 세션 생성: {new_id}")
        return new_id

    with gr.Blocks(
        title="✨ 루미 에이전트",
    ) as demo:
        # CSS 직접 삽입 (마운트 시에도 적용되도록)
        gr.HTML(f"<style>{CUSTOM_CSS}</style>")

        # 🔧 gr.State로 사용자별 세션 ID 관리
        # 페이지 로드 시 고유한 세션 ID가 생성되어 각 탭/사용자가 격리됨
        session_state = gr.State(generate_session_id)

        # 헤더
        gr.HTML(
            """
            <div class="header-container">
                <h1>✨ LUMI ✨</h1>
                <p>버추얼 아이돌 루미와 대화해보세요!</p>
            </div>
            """
        )

        # 채팅 컨테이너
        with gr.Column(elem_classes="chat-container"):
            # 채팅 인터페이스
            chatbot = gr.Chatbot(
                label="루미와 대화",
                height=450,
                elem_classes="chatbot",
                avatar_images=(
                    None,
                    "https://api.dicebear.com/9.x/adventurer/svg?seed=Lumi&hair=long16&hairColor=f06292&skinColor=fce4ec&backgroundColor=ff6b9d&eyes=variant01&eyebrows=variant01&mouth=variant01",
                ),
            )

            # 입력 영역
            with gr.Row(elem_classes="input-row"):
                msg = gr.Textbox(
                    placeholder="루미에게 메시지를 보내세요... 💭",
                    scale=4,
                    show_label=False,
                    container=False,
                )
                submit_btn = gr.Button(
                    "전송 ✨",
                    variant="primary",
                    scale=1,
                    elem_classes="send-btn",
                )

        # 빠른 응답 버튼
        gr.HTML('<div style="text-align: center; margin-top: 1rem; color: rgba(255,255,255,0.6); font-size: 0.9rem;">💡 빠른 질문</div>')
        with gr.Row(elem_classes="quick-buttons"):
            btn1 = gr.Button("👋 안녕!", elem_classes="quick-btn")
            btn2 = gr.Button("🔮 MBTI 뭐야?", elem_classes="quick-btn")
            btn3 = gr.Button("📅 이번 주 방송?", elem_classes="quick-btn")
            btn4 = gr.Button("🎵 노래 추천!", elem_classes="quick-btn")

        # 초기화 버튼
        with gr.Row():
            clear_btn = gr.Button("🗑️ 대화 초기화", elem_classes="clear-btn")

        # 이벤트 핸들러 - 2단계로 분리
        def add_user_message(message: str, chat_history: list) -> tuple:
            """1단계: 사용자 메시지 먼저 표시"""
            if not message.strip():
                return "", chat_history
            chat_history.append({"role": "user", "content": message})
            return "", chat_history

        async def get_bot_response(chat_history: list, session_id: str) -> list:
            """
            2단계: 봇 응답 생성

            Args:
                chat_history: 대화 히스토리
                session_id: 사용자별 고유 세션 ID (gr.State로 관리)
            """
            if not chat_history:
                return chat_history

            # 마지막 사용자 메시지 가져오기
            last_msg = chat_history[-1]
            if isinstance(last_msg, dict):
                last_user_msg = last_msg.get("content", "")
            else:
                last_user_msg = str(last_msg)

            if not last_user_msg:
                return chat_history

            # 🔧 session_id를 chat_with_lumi에 전달
            bot_message = await chat_with_lumi(str(last_user_msg), chat_history, session_id)
            chat_history.append({"role": "assistant", "content": bot_message})
            return chat_history

        # 전송 이벤트 - 체이닝
        # 🔧 session_state 추가 및 concurrency_limit=None으로 병렬 처리 허용
        msg.submit(
            add_user_message, [msg, chatbot], [msg, chatbot]
        ).then(
            get_bot_response,
            [chatbot, session_state],
            [chatbot],
            concurrency_limit=None,  # 🔧 여러 요청 병렬 처리 허용
        )
        submit_btn.click(
            add_user_message, [msg, chatbot], [msg, chatbot]
        ).then(
            get_bot_response,
            [chatbot, session_state],
            [chatbot],
            concurrency_limit=None,  # 🔧 여러 요청 병렬 처리 허용
        )

        # 빠른 응답 버튼 이벤트
        btn1.click(lambda: "안녕!", outputs=msg)
        btn2.click(lambda: "너 MBTI 뭐야?", outputs=msg)
        btn3.click(lambda: "이번 주 방송 일정 알려줘", outputs=msg)
        btn4.click(lambda: "신나는 노래 추천해줘", outputs=msg)

        # 🔧 클리어 시 새 세션 ID 생성 (대화 히스토리 초기화와 함께)
        def clear_chat():
            """대화 초기화 및 새 세션 ID 생성"""
            new_session_id = generate_session_id()
            return [], new_session_id

        clear_btn.click(clear_chat, outputs=[chatbot, session_state])

    return demo
