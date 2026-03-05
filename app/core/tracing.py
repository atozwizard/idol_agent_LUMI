"""
Langfuse 통합 모듈

LangGraph와 Langfuse를 연동하여 Observability를 제공합니다.

🆕 LLMOps 3강 주요 기능:
    1. LangChain CallbackHandler: 노드 실행 흐름 자동 추적
    2. trace_llm_generation(): 토큰/비용 수동 기록 (generation 타입)

사용법:
    from app.core.tracing import init_langfuse, create_langfuse_config

    # 앱 시작 시 1회 초기화
    init_langfuse()

    # LangGraph에서 사용
    config = create_langfuse_config(session_id="user-123")
    result = await graph.ainvoke(state, config=config)

토큰/비용 추적 원리:
    - LangfuseCallbackHandler: 노드를 span으로 기록 (토큰 추적 X)
    - trace_llm_generation(): generation 타입으로 기록 (토큰 추적 O)
    - Langfuse는 generation 타입에서만 토큰/비용을 계산함
"""
# [지식]
# llm 애플리케이션을 위한 오픈소스 observability(관측가능성) 플랫폼
# - trace: llm호출의 전체 흐름을 추적 (입력 -> 처리 -> 출력)
# - generation : llm 호출 단위 (토큰 수, 비용 자동계산)
# - session : 대화 세션 단위로 trace 를 그룹화

# 이 파일에서는 generation만 사용
# langfuse 는 span(일반 작업)과 generation(llm호출) 두 가지 타입을 지원하지만
# 토큰/비용 추적은 generation 타입에서만 가능
# 따라서 우리 코드에서는 trace_llm_generation()으로 generation만 기록함

# observability가 llmops에서 중요한 이유
# 프로덕션 환경에서 llm 애플리케이션을 운영하려면:
# 1. 비용추적 : 어떤 요청이 비용을 많이 사용하는지 파악
# 2. 품질 모니터링 : 응답 품질 저하를 초기에 감지
# 3. 디버깅 : 문제 발생 시 원인을 빠르게 파악
# 4. 최적화 : 병목 구간을 찾아 성능 개선

from loguru import logger

from app.core.config import settings

# Langfuse 전역 초기화
# langfuse 클라이언트는 앱 전체에서 하나만 있으면 되므로 싱글톤 패턴을 사용.
# 이 플래그로 중복 초기화를 방지
_langfuse_initialized = False


# 싱글톤 패턴?
# 클래스의 인스턴스가 오직 하나만 존재하도록 보장하는 디자인 패턴
# langfuse 클라이언트처럼 전역적으로 하나만 필요한 객체에 적합
# 여러번 초기화해도 같은 인스턴스를 반환하여 리소스낭비를 방지


def init_langfuse():
    """
    Langfuse 전역 초기화 (앱 시작 시 1회)

    Returns:
        Langfuse | None: 초기화된 Langfuse 클라이언트 또는 None
    """
    global _langfuse_initialized

    if _langfuse_initialized:  # True
        return get_langfuse_client()

    # TODO 1: API 키 확인 및 Langfuse 클라이언트 초기화
    if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
        logger.warning("[langfuse] api 키가 설정되지 않아 비활성화됩니다.")
        return None

    try:
        from langfuse import Langfuse, get_client

        # langfuse 클라이언트 초기화
        # - public_key, secret_key: langfuse 프로젝트의 api키
        # - host : cloud(http://cloud.langfuse.com) 또는 self-hosted url
        # - flush_interval : 이벤트를 서버로 전송하는 주기 (초)
        #   - 값이 작으면 : 실시간성 좋지만 네트워크 부하 증가
        #   - 값이 크면 : 배치 처리로 효율적이지만 앱 종료시 데이터 손실 가능
        Langfuse(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_BASE_URL,
            flush_interval=settings.langfuse_flush_interval,
        )

        _langfuse_initialized = True
        logger.info(f"[langfuse] 클라이언트 초기화 완료: {settings.LANGFUSE_BASE_URL}")

        # get_client()
        # langfuse sdk 전역 클라이언트를 관리합니다.
        # langfuse()로 초기화하면 내부적으로 전역 클라이언트가 설정되고
        # get_client()로 어디서든 접근할 수 있다.
        return get_client()

    except Exception as e:
        logger.error(f"[langfuse]: 클라이언트 초기화 실패: {e}")
        return None


def get_langfuse_client():
    """
    Langfuse 클라이언트 싱글톤 반환

    Returns:
        Langfuse | None: Langfuse 클라이언트 또는 None
    """
    global _langfuse_initialized

    if not _langfuse_initialized:
        return init_langfuse()

    try:
        from langfuse import get_client

        return get_client()
    except Exception as e:
        logger.warning(f"⚠️ [Langfuse] 클라이언트 가져오기 실패: {e}")
        return None


# [지식] langchain callbackhandler
# langchain 에서 llm 호출, 체인 실행 등의 이벤트를 감지하는 메커니즘.
# callbackhandler를 config에 전달하면 langchain이 자동으로 이벤트를 캡처
# langfuse 의 callbackhandler는 이 이벤트들을 langfuse서버로 전송함
def get_langfuse_handler():
    """
    LangChain 콜백 핸들러 생성

    CallbackHandler는 파라미터 없이 생성합니다.
    session_id, user_id는 config["metadata"]에 langfuse_ prefix로 전달합니다.

    Returns:
        CallbackHandler | None: Langfuse 콜백 핸들러 또는 None
    """
    # TODO 2: Langfuse 콜백 핸들러 생성
    if not settings.enable_langfuse:
        return None
    langfuse = get_langfuse_client()
    if langfuse is None:
        return None

    try:
        # langfuse.langchain.callbackhandler # 이 줄을 삭제하고 핸들러 생성 로직을 작성하세요!
        # langchain과 langfuse를 연결하는 브릿지 역할
        # 이 핸들러를 langgraph의 config에 전달하면 노드실행 흐름이 기록됨

        # 주의 : 우리는 litellm 래퍼를 사용하므로
        # callbackhandler만으로는 토큰/비용이 자동 추적되지 않음.
        # 따라서 trace_llm_generation()을 별도로 호출하여 토큰을 기록해야함
        from langfuse.langchain import CallbackHandler

        handler = CallbackHandler()
        logger.debug("[langfuse] 핸들러 생성 완료")
        return handler

    except Exception as e:
        logger.error(f"[langfuse] 핸들러 생성 실패: {e}")
        return None


# def create_langfuse_config(
#     session_id: str,
#     user_id: str | None = None,
#     tags: list[str] | None = None,
# ) -> dict:
#     """
#     Langfuse 메타데이터가 포함된 config 생성

#     Args:
#         session_id: 세션 ID (대화 그룹화용)
#         user_id: 사용자 ID (선택)
#         tags: 태그 목록 (선택)


#     Returns:
#         dict: LangGraph config (callbacks + metadata)
#     """
# TODO 3: LangGraph용 config 생성
# langgraph config
# langgraph에서 그래프 실행시 전달하는 설정 딕셔너리
# - configurable : thread_id 등 langgraph 내부 설정
# - callbacks : langchain callbackhandler 리스트
# - metadata: langfuse에 전달할 메타데이터 (langfuse_prefix 필요)
# 이 줄을 삭제하고 config 생성 로직을 작성하세요!
def create_langfuse_config(
    session_id: str,
    user_id: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """
    langfuse 메타데이터가 포함된 config 생성
    args:
        session_id : 세션 ID (대화 그룹화용)
        user_id : 사용자 ID(선택)
        tags : 태그 목록(선택)

    returns:
        dict: langgraph config (callbacks + metadata)
    """
    handler = get_langfuse_handler()
    if handler is None:
        return {}

    default_tags = [settings.environment, "lumi-chat"]
    if tags:
        default_tags.extend(tags)

    # [설명] langfuse_ prefix 규칙
    # langfuse callbackhandler는 metadata에서 "langfuse_" prefix가 붙은 키만 인식함.
    # - langfuse_session_id : 같은 세션의 trace를 그룹화
    # - langfuse_user_id : 사용자별 분석 기능
    # - langfuse_tags : 필터링 및 분류용 태그
    metadata = {
        "langfuse_session_id": session_id,
        "langfuse_tags": default_tags,
    }
    if user_id:
        metadata["[langfuse_user_id]"] = user_id
    # [설명] config 구조
    # langgraph의 ainvoke/astream에 전달하는 config입니다.
    # callbacks 리스트에 핸들러를 넣으면 자동으로 추적이 시작됩니다
    return {
        "callbacks": [handler],
        "metadata": metadata,
    }


# 왜 수동으로 generation을 기록해야 하는가?
# langfusecallbackhandler는 langchain 표준 llm(chatopenai 등)을 사용할 때만
# 자동으로 generation을 기록합니다. 우리는 litellm 커스텀 래퍼를 사용하므로
# callbackhandler가 토큰 정보를 인식하지 못합니다.
# 따라서 수동으로 trace_llm_generation()을 호출하여 토큰/비용을 기록합니다.


def trace_llm_generation(
    session_id: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    input_content: str | None = None,
    output_content: str | None = None,
    user_id: str | None = None,
):
    """
    🆕 LLMOps 3강: LLM 호출을 Langfuse generation으로 기록

    Langfuse에서 토큰/비용을 추적하려면 observation 타입이 'generation'이어야 합니다.
    LangfuseCallbackHandler는 span으로 기록되어 토큰 추적이 안 되므로,
    수동으로 generation을 생성합니다.

    Args:
        session_id: 세션 ID
        model: 모델명 (예: "solar-pro2", "openai/solar-pro2")
        input_tokens: 입력 토큰 수
        output_tokens: 출력 토큰 수
        input_content: 입력 내용 (선택)
        output_content: 출력 내용 (선택)
        user_id: 사용자 ID (선택)

    Note:
        - OpenAI 호환 스키마 사용: prompt_tokens, completion_tokens, total_tokens
        - Langfuse가 자동으로 input → prompt_tokens 등으로 매핑
    """
    langfuse = get_langfuse_client()
    if langfuse is None:
        return

    try:
        total_tokens = input_tokens + output_tokens

        # Langfuse v3: start_as_current_observation으로 generation 기록
        # as_type="generation"으로 설정해야 토큰/비용 추적 가능!

        # lanffuse v3 context manager api
        # start_as_current_observaton()은 context manager로 observation을 생성합니다
        # - as_type="generation": llm호출임을 명시 -> 토큰/비용 대시보드에 표시
        # - name: langfuse ui에 표시될 이름
        # - model: 사용된 모델명 (비용 계산에 사용)
        with langfuse.start_as_current_observation(
            as_type="generation",
            name="llm-response",
            model=model,
            input=input_content,
        ) as generation:
            # trace에 session_id, user_id 설정
            # updatd_trace()로 trace 레벨 메타데이터 설정
            # generation은 trace 안에 포함되며, trace에 session_id를 설정하면
            # 같은 세션의 모든 trace를 그룹화하여 볼 수 있습니다.

            generation.update_trace(
                session_id=session_id,
                user_id=user_id,
            )

            # usage_details로 토큰 정보 전송
            # OpenAI 호환 스키마: prompt_tokens, completion_tokens

            # usage_details와 openai 호환 스키마
            # langfuse는 openai 스타일의 토큰 필드명을 사용합니다:
            # - prompt_tokens: 입력 토큰(= input_tokens)
            # - completion_tokens: 출력 토큰(= output_tokens)
            # - total_tokens: 전체 토큰
            # 이 정보를 기반으로 langfuse가 비용을 자동 계산합니다

            generation.update(
                output=output_content,
                usage_details={
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": total_tokens,
                },
            )

        logger.debug(
            f"📊 [Langfuse] LLM generation 기록: {model}, "
            f"tokens={input_tokens}+{output_tokens}={total_tokens}"
        )

    except Exception as e:
        logger.error(f"❌ [Langfuse] LLM generation 기록 실패: {e}")


# [지식] 버퍼 플러시(buffer flush)
# langfuse 는 성능을 위해 이벤트를 즉시 전송하지 않고 버퍼에 모아둡니다.
# flush_interval마다 자동으로 전송되지만, 앱이 갑자기 종료되면 데이터 손실 가능!
# 따라서 앱 종료 시 명시적으로 flush()를 호출하여 남은 이벤트를 모두 전송합니다.


def flush_langfuse():
    """
    Langfuse 버퍼 플러시 (앱 종료 시 호출)
    """
    langfuse = get_langfuse_client()
    if langfuse is None:
        return

    try:
        langfuse.flush()
        logger.info("🔄 [Langfuse] 버퍼 플러시 완료")
    except Exception as e:
        logger.error(f"❌ [Langfuse] 플러시 실패: {e}")
