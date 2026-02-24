#router -> rag -> tool

from pydantic import BaseModel, Field
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
from typing import Literal
from app.core.prompts import ROUTER_PROMPT
from app.core.config import settings
from app.graph.state import LumiState
from loguru import logger
from app.repositories.rag import get_rag_repository
from app.graph.state import LumiState


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
    """
    logger.info("[RAG] 문서 검색 시작")
    
    last_message = state["messages"][-1]
    user_input = last_message.content
    
    try:
        # RAG에 대한 결과를 가지고오면 됨
        rag_repo = get_rag_repository()
        docs = await rag_repo.search_simailar(
            query=user_input,
            k=3,
            filter_status="active"
        )
        
        retrieved_docs = [["content"] for doc in docs]
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

    print(f"[Tool] 실행: {tool_name}, 인자: {tool_args}")

    # 실제로는 DB 조회, API 호출 등을 해야 함
    # Tool 실행을 전담하는 Tool Executor 클래스를 만들어서 분리하자!
 
    tool_executor.execute()