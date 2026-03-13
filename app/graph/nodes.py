# router -> rag -> tool
"""
LangGraph 그래프의 노드(Node) 정의

노드는 그래프에서 실제 작업을 수행하는 단위입니다.
각 노드는 State를 받아서 업데이트할 필드만 반환합니다.

이 파일에서 정의하는 노드:
    1. router_node: 사용자 의도 분류 (chat/rag/tool)
    2. rag_node: 문서 검색 및 컨텍스트 생성
    3. tool_node: Tool 실행
    4. response_node: 최종 응답 생성
"""

import asyncio
import json
from datetime import datetime
from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

# langchain/langgraph 에서 실행 설정을 전달하는 타입, 노드 함수의 파라미터로 전달
from loguru import logger
from pydantic import BaseModel, Field

# from app.core.config import get_llm
from app.core.config import settings
from app.core.cost_tracker import get_cost_tracker
from app.core.llm import get_router_llm
from app.core.prompts import RAG_RESPONSE_PROMPT, RESPONSE_PROMPT, ROUTER_PROMPT
from app.core.token_counter import count_messages_tokens, count_tokens
from app.core.tracing import trace_llm_generation
from app.graph.state import LumiState
from app.repositories.conversation import get_conversation_repository
from app.repositories.rag import get_rag_repository
from app.tools.executor import ToolExecutor

TOOL_EXECUTION_TIMEOUT = 10


class RouterOutput(BaseModel):
    """
    라우터 노드의 출력 스키마

    LLM이 JSON 파싱 없이 직접 이 형식으로 응답합니다.
    with_structured_output()을 사용하면 자동으로 파싱됩니다.
    """

    intent: Literal["chat", "rag", "tool"] = Field(
        description="사용자 의도: chat(일반대화), rag(정보검색), tool(도구실행)"
    )
    tool_name: str | None = Field(
        default=None, description="실행할 도구 이름 (intent=tool일 때만)"
    )
    tool_args: dict | None = Field(
        default=None, description="도구 실행 인자 (intent=tool일 때만)"
    )


# def get_llm() -> ChatUpstage:
#     """upstage solar LLM 클라이언트를 반환"""
#     return ChatUpstage(
#         api_key=settings.UPSTAGE_API_KEY,
#         model=settings.llm_model,
#         timeout=30,
#         max_retries=2,
#     )


tool_executor = ToolExecutor()


# ============================================================
# 🆕 LLMOps 2강: 메시지 트리밍 함수
# ============================================================
def trim_messages(
    messages: list[BaseMessage],
    max_tokens: int | None = None,
) -> list[BaseMessage]:
    """
    🆕 LLMOps 2강: Context Window 관리를 위한 메시지 트리밍

    대화가 길어지면 Context Window를 초과할 수 있습니다.
    오래된 메시지를 제거하여 토큰 수를 제한합니다.

    트리밍 규칙:
        1. SystemMessage는 항상 유지 (루미의 정체성!)
        2. 최근 메시지부터 역순으로 토큰 계산
        3. max_tokens 초과하면 오래된 메시지 제거

    Args:
        messages: LangChain 메시지 리스트
        max_tokens: 최대 토큰 수 (기본값: settings.max_context_tokens)

    Returns:
        List[BaseMessage]: 트리밍된 메시지 리스트

    Example:
        >>> trimmed = trim_messages(state["messages"])
        >>> # 최근 메시지만 포함된 리스트 반환
    """
    if max_tokens is None:
        max_tokens = settings.max_context_tokens

    # SystemMessage 분리 (항상 유지)
    system_messages = [m for m in messages if isinstance(m, SystemMessage)]
    other_messages = [m for m in messages if not isinstance(m, SystemMessage)]

    # SystemMessage 토큰 수 계산
    system_tokens = count_messages_tokens(system_messages) if system_messages else 0
    available_tokens = max_tokens - system_tokens

    if available_tokens <= 0:
        logger.warning("⚠️ SystemMessage만으로 max_tokens 초과! SystemMessage만 반환")
        return system_messages

    # TODO 1 : 메시지 트리밍 로직 구현
    # 최근 메시지부터 역순으로 토큰을 계산하여, available_tokens를 초과하지 않는 메시지만 유지합니다.
    # 왜 역순으로 처리할까?
    # 오래된 메시지부터 지워야 최근 대화를 보존할 수 있기 때문
    # 정방향으로 처리하면 예전 메시지만 남고 최근 맥락이 잘림
    trimmed = []
    total_tokens = 0
    for msg in reversed(other_messages):
        # 메시지 토큰 수(오버헤드 4토큰 포함)
        msg_tokens = count_tokens(msg.content) + 4

        if total_tokens + msg_tokens > available_tokens:
            # 토큰 초과 -> 여기서 중단
            break

        trimmed.insert(0, msg)  # 역순으로 추가했으므로 앞에 삽입
        total_tokens += msg_tokens

    # 트리밍 결과 로깅
    original_count = len(other_messages)
    trimmed_count = len(trimmed)
    if original_count != trimmed_count:
        logger.info(
            f"✂️ 메시지 트리밍: {original_count} → {trimmed_count} "
            f"(토큰: {total_tokens}/{available_tokens})"
        )

    return system_messages + trimmed


async def router_node(state: LumiState, config: RunnableConfig) -> dict:
    """사용자 의도 분류"""
    logger.info("[Router] 의도 분류 시작")
    last_message = state["messages"][-1]
    user_input = last_message.content

    llm = get_router_llm()
    # get_llm -> solar-pro2. 사용자 의도 분류 task -> routernode. 성능이 엄청 좋은 모델을 사용할 필요가 없음
    # 조금 성능이 떨어져도 빠르고 저렴한 모델을 사용
    structured_llm = llm.with_structured_output(RouterOutput)
    current_date = datetime.now().strftime("%Y-%m-%d")

    messages = [
        HumanMessage(content=f"오늘 날짜: {current_date}\n\n{ROUTER_PROMPT}"),
        HumanMessage(content=f"사용자: {user_input}"),
    ]

    try:
        result = await structured_llm.ainvoke(messages, config=config)
        # tool_name 정리
        # LLm은 가끔 예상하지 못하는 형식으로 응답
        # 따옴표 포함 -> get_schedule,
        # 여러 도구 나열 : "get_schedule, recommend_song"
        # 너무 긴 문자열 : aaabcasasdfasdhhk
        # 방어 로직을 만들어서 안정적인 서비스를 제공
        tool_name = result.tool_name
        if tool_name:
            # 비정상적으로 긴 tool_name 필터링.
            if len(tool_name) > 50:
                logger.warning(f"tool_name 이 너무 김. ({len(tool_name)}자, 무시)")
                tool_name = None
            else:
                # 따옴표를 제거 -> 유니코드 따옴표
                tool_name = tool_name.strip()
                quote_chars = "'\"`'''\"\"「」『』"
                tool_name = tool_name.strip(quote_chars)
                for char in quote_chars:
                    tool_name = tool_name.replace(char, "")

                # 쉼표로 나열된 경우 첫번째만 사용
                if "," in tool_name:
                    tool_name = tool_name.split(",")[0].strip()
                # tool1?tool2?tool3
                if "?" in tool_name:
                    tool_name = tool_name.split("?")[0].strip()

        # 유효한 tool 이름만 나오는지 화이트리스트
        vaild_tools = [
            "get_schedule",
            "send_fan_letter",
            "recommend_song",
            "get_weather",
        ]

        result_intent = result.intent

        if result_intent == "tool":
            if not tool_name:
                logger.warning("intent=tool 인데 tool_name이 없음, chat 으로 전환")
                result_intent = "chat"
            elif tool_name not in vaild_tools:
                logger.warning(f"유효하지 않은 tool: {tool_name}, chat으로 전환")
                tool_name = None
                result_intent = "chat"

        logger.debug(
            f"LLM 응답 (structured) : intent={result.intent},"
            f" tool_name={result.tool_name}, tool_args={result.tool_name}"
        )

        logger.info(f"[Router] 의도: {result.intent}, 도구: {result.tool_name}")
        return {
            "intent": result.intent,
            "tool_name": result.tool_name,
            "tool_args": result.tool_args,
        }
    except Exception as e:
        logger.warning(f"[Router] 노드 오류: {e}, 기본값(chat)으로 설정")
        return {"intent": "chat", "tool_name": None, "tool_args": None}


async def rag_node(state: LumiState) -> dict:
    """
    RAG노드 : 관련 문서 검색
        Supabase pgvector를 사용한 RAG 구현
    - 활성 문서(v2.5)만 검색하여 폐기 문서(v1.0) 제외
    - 메타데이터 필터링으로 세계관 일관성 유지

    Args:
        state: 현재 에이전트 상태

    Returns:
        dict: 업데이트할 상태 필드
            - retrieved_docs: 검색된 문서 내용 목록
    """
    logger.info("[RAG] 문서 검색 시작")

    last_message = state["messages"][-1]
    user_input = last_message.content

    try:
        # RAG에 대한 결과를 가지고오면 됨
        rag_repo = get_rag_repository()
        docs = await rag_repo.search_similar(
            query=user_input, k=3, filter_status="active"
        )
        # 검색결과에서 content만 추출
        retrieved_docs = ["content" for doc in docs]

        # 검색 결과 로깅 (디버깅용)
        for i, doc in enumerate(docs):
            version = doc.get("metadata", {}).get("version", "?")
            similarity = doc.get("similarity", 0)
            logger.debug(
                f"  [{i + 1}] v{version} (sim: {similarity:.3f}): {doc['content'][:50]}..."
            )

        logger.info(f"[RAG] 검색 완료: {len(retrieved_docs)}개 문서")

    except Exception as e:
        logger.error(f"[RAG] 검색 실패: {e}")
        # 에러를 알려주고 대응,
        retrieved_docs = [
            "루미는 프리즘 행성 출신 외계인 공주야",
            "루미의 팬덤은 '루미너스(Luminous)'야!",
        ]

    return {"retrieved_docs": retrieved_docs}


async def tool_node(state: LumiState) -> dict:
    """
    Tool 노드 : tool 실행.
    LLM이 외부 시스템과 상호작용할 수 있게 해주는 기능

    llmops 1강 : 타임아웃 및 에러 핸들링 추가
    """
    tool_name = state["tool_name"]
    tool_args = state["tool_args"] or {}

    # 방어 코드: tool_name이 None이면 에러 반환
    if not tool_name:
        logger.error("🔧 [Tool] tool_name이 None!")
        return {
            "tool_result": {
                "success": False,
                "error": "Tool 이름이 지정되지 않았어요.",
            },
        }

    print(f"[Tool] 실행: {tool_name}, 인자: {tool_args}")

    # 실제로는 DB 조회, API 호출 등을 해야 함
    # Tool 실행을 전담하는 Tool Executor 클래스를 만들어서 분리하자!
    try:
        # asyncio.wait_for : 비동기 작업에 타임아웃을 설정하는 방법
        # timeout 초과시 asyncio.TimeoutError 발생
        # 이를 통해 외구 api 호출이 무한 대기하는 것을 방지
        result = await asyncio.wait_for(
            tool_executor.execute(
                tool_name=tool_name,
                tool_args=tool_args,
                session_id=state["session_id"],
                user_id=state.get("user_id"),
            ),
            timeout=TOOL_EXECUTION_TIMEOUT,
        )

        logger.info(f"[Tool] 실행 결과: {result}")

        return {"tool_result": result}
    except TimeoutError:
        logger.warning(
            f"[Tool] 타임아웃: {tool_name} 실행 시간이 {TOOL_EXECUTION_TIMEOUT}초 초과"
        )
        return {
            "tool_result": {
                "success": False,
                "error": "timeout",
                "message": "잠시 기다려줘! 정보를 가져오는데 시간이 좀 걸리고 있어..나중에 다시 물어봐줄래?",
            }
        }
    except Exception as e:
        logger.error(f"[Tool] 실행 실패: {tool_name} - {e}")
        return {
            "tool_result": {
                "success": False,
                "error": str(e),
                "message": f"앗, '{tool_name}' 기능에 문제가 생겼어! 나중에 다시 시도해줄래?",
            }
        }


async def response_node(state: LumiState, config=RunnableConfig) -> dict:
    """최종 응답 생성
    chat: 일반대화
    rag :검색된 문서 기반 응답
    tool : Tool결과 기반

    💬 응답 노드: 최종 응답 생성

    라우팅 결과에 따라 적절한 응답을 생성합니다:
        - chat: 일반 대화 응답
        - rag: 검색된 문서 기반 응답
        - tool: Tool 결과 기반 응답

    Args:
        state: 현재 에이전트 상태

    Returns:
        dict: 업데이트할 상태 필드
            - messages: AI 응답 메시지 추가
    """
    logger.info(f"💬 [Response] 응답 생성 시작 (intent: {state['intent']})")
    # print(state,"="*50)
    llm = get_router_llm()

    user_input = state["messages"][-1].content

    intent = state["intent"]

    if intent == "rag":
        context = "\n".join(state["retrieved_docs"])
        system_prompt = RAG_RESPONSE_PROMPT.format(context=context)

    elif intent == "tool":
        tool_result = state["tool_result"]
        tool_name = state["tool_name"]

        # tool 에러시 조기 반환
        # tool 실패 -> llm을 호출하지 않고 바로 에러메시지 반환
        # llm api 비용 절약, 빠른 응답
        # 일관된 에러메시지
        if tool_result.get("success") is False:
            error_message = tool_result.get(
                "message", "문제가 생겼어! 나중에 다시 시도해줄래?"
            )
            logger.info(f"🚨 [response] tool error -> 바로 반환: {error_message}")
            return {"messages": [AIMessage(content=error_message)]}
        result_context = f"""
## 📋 조회 결과 (내부 참고용, 절대 그대로 출력하지 마!)
tool_name : {tool_name}, tool_result :{json.dumps(tool_result, ensure_ascii=False, indent=2)}

## 규칙
- 위 결과를 바탕으로 루미답게 친근하게 안내해줘
- 성공한 경우: 결과를 자연스럽게 전달 (예: "이번 주 금요일에 뮤직뱅크 나와!")
- 실패한 경우: 부드럽게 안내 (예: "흠, 지금은 일정이 없나봐!")
- ❌ "get_schedule", "tool", "실행 결과" 같은 기술 용어 절대 금지!
        """
        system_prompt = RESPONSE_PROMPT + result_context
    else:
        system_prompt = RESPONSE_PROMPT

    trimmed_messages = trim_messages(state["messages"])
    # 대화 히스토리 관리, 과거 대화를 전달하면 맥락을 이해하면 좋겠음

    # 대화 히스토리를 LLM에 전달하여 과거 질문 기억
    # 최근 6개 메시지 (3턴: user+ai 쌍)를 히스토리로 포함
    # 마지막 메시지(현재 질문)는 별도로 추가하므로 제외
    history_messages = trimmed_messages[:-1][-6:] if len(trimmed_messages) > 1 else []

    # 히스토리를 텍스트로 변환
    history_text = ""
    if history_messages:
        history_parts = []
        for msg in history_messages:
            role = "사용자" if isinstance(msg, HumanMessage) else "루미"
            history_parts.append(f"{role}: {msg.content}")
        history_text = "\n".join(history_parts)
        history_text = f"\n\n## 이전 대화:\n{history_text}\n"

    messages = [
        HumanMessage(content=system_prompt + history_text),
        HumanMessage(content=f"사용자: {user_input}"),
    ]
    input_tokens = count_messages_tokens(messages)

    try:
        response = await llm.ainvoke(messages, config=config)
        ai_response = response.content

        used_model = settings.llm_model
        if hasattr(response, "response_metadata") and response.response_metadata:
            used_model = response.response_metadata.get(
                "model_name", settings.llm_model
            )

        output_tokens = count_tokens(ai_response)

        # 비용 추적, 일일 비용 한도 초과 시 dissord 알림 발송
        try:
            cost_tracker = get_cost_tracker()
            await cost_tracker.track_usage(
                session_id=state["session_id"],
                model=used_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        except Exception as e:
            logger.error(f"비용 추적 실패 (무시): {e}")

        # langfuse generation 기록
        # 수동으로 generation 기록해서 토큰/비용 추적
        try:
            trace_llm_generation(
                session_id=state["session_id"],
                model=used_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_content=user_input,
                output_content=ai_response,
                user_id=state["user_id"],
            )
        except Exception as e:
            logger.warning(f"langfuse generation 기록 실패 (무시) {e}")
        # 대화 저장
        try:
            conversation_repo = get_conversation_repository()
            await conversation_repo.save_turn(
                session_id=state["session_id"],
                user_message=user_input,
                assistant_message=ai_response,
                intent=intent,
                tool_name=state.get("tool_name"),
                tool_result=state.get("tool_result"),
                metadata={"input_tokens": input_tokens, "output_tokens": output_tokens},
            )
        except Exception as e:
            logger.error(f"대화 저장 실패 (무시): {e}")

    except Exception as e:
        logger.error(f"응답 생성 오류: {e}")
        ai_response = "미안, 오류가 생겼어! 다시 말해줄래?"

    logger.info("💬 [Response] 응답 생성 완료")
    return {"messages": [AIMessage(content=ai_response)]}
