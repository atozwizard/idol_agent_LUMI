"""채팅 api 라우트
langgraph에이전트를 호출하여 사용자 메시지를 처리"""

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
from loguru import logger


from app.schemas.chat import ChatRequest, ChatResponse
from app.graph import get_lumi_graph


router = APIRouter()

@router.post("/", response_model=ChatResponse)

async def chat(request : ChatRequest) -> ChatResponse:
    
    """채팅 엔드포인트
    사용자 메시지를 langgraph 에이전트로 처리하고 응답을 반환합니다."""
    
    logger.info(f"채팅 요청: session={request.session_id}, message={request.message[:50]}")
    try:
        #step1 : langgraph 그래프 가져오기
        graph = get_lumi_graph()
        
        #step2 : 초기 state 생성
        initial_state = {
            "messages":[HumanMessage(content=request.message)],
            "intent" : None,
            "retrieved_docs": [],
            "tool_name": None,
            "tool_args": None,
            "tool_result": None,
            "session_id": request.session_id,
            "user_id": request.user_id
        }
        #step3 : 그래프 실행
        logger.debug("LangGraph 실행 시작")
        final_state = await graph.ainvoke(initial_state)
        logger.debug("LangGraph 실행 완료")
        #step4 : 최종 응답 추출
        messages = final_state["messages"]
        if len(messages) < 2:
            raise ValueError("응답 메시지가 없습니다.")
        
        ai_response = messages[-1].content
        tool_used = final_state.get("tool_name")
        
        return ChatResponse(
            message=ai_response,
            tool_used=tool_used,
            cached=False
        )
        
    except Exception as e:
        logger.error(f"채팅 처리 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"에이전트 처리 중 오류가 발생했습니다. {str(e)}" 
        )