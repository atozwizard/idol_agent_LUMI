#router -> rag -> tool
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
from pydantic import BaseModel, Field
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
from typing import Literal
from app.core.prompts import ROUTER_PROMPT , RESPONSE_PROMPT, RAG_RESPONSE_PROMPT
from app.core.config import settings
from app.graph.state import LumiState
from loguru import logger
from app.repositories.rag import get_rag_repository
from app.graph.state import LumiState
from app.tools.executor import ToolExecutor
import json
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


def get_llm() -> ChatUpstage:
    """upstage solar LLM 클라이언트를 반환"""
    return ChatUpstage(
        api_key=settings.upstage_api_key, 
        model=settings.llm_model,
        timeout=30,
        max_retries=2
    )

tool_executor = ToolExecutor()

async def router_node(state: LumiState) -> dict:
    """사용자 의도 분류"""
    logger.info("[Router] 의도 분류 시작")
    last_message = state["messages"][-1]
    user_input = last_message.content

    llm = get_llm()
    structured_llm = llm.with_structured_output(RouterOutput)
    current_date = datetime.now().strftime("%Y-%m-%d")

    messages = [
        HumanMessage(content=f"오늘 날짜: {current_date}\n\n{ROUTER_PROMPT}"),
        HumanMessage(content=f"사용자: {user_input}"),
    ]

    try:
        result = await structured_llm.ainvoke(messages)
        logger.debug(
            f"LLM 응답 (structured) : intent={result.intent},"
            f" tool_name={result.tool_name}, tool_args={result.tool_name}")
        
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
            query=user_input,
            k=3,
            filter_status="active"
        )
        # 검색결과에서 content만 추출
        retrieved_docs = [["content"] for doc in docs]
        
        # 검색 결과 로깅 (디버깅용)
        for i, doc in enumerate(docs):
            version = doc.get("metadata", {}).get("version", "?")
            similarity = doc.get("similarity", 0)
            logger.debug(f"  [{i+1}] v{version} (sim: {similarity:.3f}): {doc['content'][:50]}...")

        
        logger.info(f"[RAG] 검색 완료: {len(retrieved_docs)}개 문서")
        
    except Exception as e:
        logger.error(f"[RAG] 검색 실패: {e}")
        # 에러를 알려주고 대응,
        retrieved_docs = [
            "루미는 프리즘 행성 출신 외계인 공주야",
            "루미의 팬덤은 '루미너스(Luminous)'야!"
        ]
        
    return {"retrieved_docs": retrieved_docs}



async def tool_node(state: LumiState) -> dict:
    """
    Tool 노드 : tool 실행.
    LLM이 외부 시스템과 상호작용할 수 있게 해주는 기능
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

    result = await tool_executor.execute(
        tool_name = tool_name,
        tool_args=tool_args,
        session_id=state["session_id"],
        user_id=state.get("user_id")
    
    )
    
    logger.info(f"[Tool] 실행 결과: {result}")
    
    return {
        "tool_result": result
    }
    
    




async def response_node(state: LumiState) -> dict:
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
    
    llm = get_llm()
    user_input = state["messages"][-1].content
    
    intent = state["intent"]

    if intent == "rag":
        context = "\n".join(state["retrieved_docs"])
        system_prompt = RAG_RESPONSE_PROMPT.format(context=context)
        
    elif intent == "tool":
        tool_result = state["tool_result"]
        tool_name = state["tool_name"]
        
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
    #대화 히스토리 관리, 과거 대화를 전달하면 맥락을 이해하면 좋겠음
    
    # 대화 히스토리를 LLM에 전달하여 과거 질문 기억
    # 최근 6개 메시지 (3턴: user+ai 쌍)를 히스토리로 포함
    # 마지막 메시지(현재 질문)는 별도로 추가하므로 제외
    history_messages = state["messages"][:-1][-6] if len(state["messages"]) > 1 else []
    
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

    try:
        response = await llm.ainvoke(messages)
        logger.info(f"💬 [Response] 응답 생성 완료")
        return {"messages": [AIMessage(content=response.content)]}
    
    except Exception as e:
        logger.error(f"응답 생성 오류: {e}")
        return {"messages": [AIMessage(content=f"미안, 오류가 생겼어! 다시 말해줄래? ({e})")]}


