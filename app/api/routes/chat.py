"""채팅 api 라우트
langgraph에이전트를 호출하여 사용자 메시지를 처리

엔드포인트:
    POST /chat/          - 채팅 메시지 전송
"""

from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage
from loguru import logger


from app.schemas.chat import ChatRequest, ChatResponse, StreamEvent
from app.graph import get_lumi_graph


router = APIRouter()

# In_memory 세션 저장소
# 서버 메모리에 세션별 대화 히스토리를 저장
# 장점 : 빠른 접근 속도, 구현 간단

SESSION_STORE : dict[str, list[BaseMessage]] = {}


@router.post("/", response_model=ChatResponse)

async def chat(request : ChatRequest) -> ChatResponse:
    
    """채팅 엔드포인트
    사용자 메시지를 langgraph 에이전트로 처리하고 응답을 반환합니다.
    
    Args:
        request: 채팅 요청 (message, session_id, user_id)

    Returns:
        ChatResponse: 루미의 응답

    Raises:
        HTTPException: 에이전트 처리 오류 시

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/chat/" \\
            -H "Content-Type: application/json" \\
            -d '{"message": "오늘 방송 언제야?", "session_id": "user123"}'
    """
    
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
            "tool_args": {},
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
        
# SSE
# 서버에서 클라이언트로 단방향 실시간 데이터를 전송하는 http 기반 프로토콜
# websocket과 달리 단방향이지만, http/1.1 위에서 동작해서 구현이 간단
# 형식 : "data: {JSON}\n\n" 형태로 이벤트를 전송

#SSE 스트리밍을 위한 helper 함수
async def stream_with_status(
        message: str,
        session_id: str,
        user_id: str | None = None
) -> AsyncGenerator[tuple[str |None, str |None, str|None, str| None], None]:
    # AsyncGenerator : Generator의 비동기버전
    # Generator는 yield 를 쓰는 함수
    # yield : generator가 값을 하나씩 뱉는 방법
    # 함수 => return: 한번에 값을 반환, 포장주문
        # yield : 하나 만들면 바로 반환, 또 하나 만들면 반환, 회전초밥
    """노드 상태 + 토큰 스트리밍 결합
    
    진행상황을 표시하면서 토큰도 스트리밍
    tuple : 칸이 4개면 tuple
    (status, token, final_response, tool_used)
    - (status, None, None, None) : 진행 상황 메시지
    - (None, None, None, None) : 스트리밍 중인 토큰
    - (None, None, final_Response, tool_used) : 최종 응답
    
    """
    
    graph = get_lumi_graph()
    
    session_id = session_id or "default"
    history = SESSION_STORE.get(session_id, [])
    new_massage = HumanMessage(content=message)
    
    initial_state = {
        "messages" : history + [new_massage],
        "intent":None,
        "retrieved_docs": [],
        "tool_name": None,
        "tool_args": {},
        "tool_result": None,
        "session_id": session_id,
        "user_id": user_id
    }
    
    logger.debug(f"[StreamWithStatus] 세션 히스토리: {len(history)}개 메시지")
    
    final_response = ""
    final_tool_name = None
    current_node = None
    
    # 노드 이름 -> 사용자 친화적 메시지
    node_status ={
        "router" : "루미 생각 중...",
        "rag": "정보 검색 중...",
        "tool":"도구 실행 중...",
        "response": "응답 작성 중..."
    }
    
    async for mode, event in graph.astream(initial_state, stream_mode=["updates", "messages"]):
        # stream_mode = updates -> 노드 스트리밍. 노드가 완료 될 때마다 이벤트를 발생
        if mode == "updates":
            # event ={"router": {"next": "tool"}}
            for node_name, node_output in event.items():
                # 새로운 노드 진입
                if node_name != current_node and node_name in node_status:
                    current_node = node_name
                    yield (node_status[node_name], None, None, None)
                    logger.debug(f"[StreamWithStatus] 노드 진입: {node_name}")
                    
                # tool 노드에서 tool_name 추출
                if node_name == "tool" and node_output:
                    final_tool_name = node_output.get("tool_name")
        
        # 토큰 스트리밍(stream_mode="messages"): LLM이 토큰을 생성할 때마다 이벤트 발생           
        elif mode == "messages":
            # event = (message, metadata) 튜플
            msg, meta = event
            node_name = meta.get("langgraph_node", "")
            
            # response 노드의 토큰만 스트리밍(router 노드 토큰은 무시)
            if node_name != "response":
                continue
            
            if isinstance(msg, AIMessageChunk):
                #AIMessageChunk : 토큰 하나하나
                # 안, 녕, 하, 세, 요
                token = msg.content or ""
                if token:
                    final_response += token
                    yield (None, token, None, None)
    
    
    # 세션 히스토리에 저장                
    if final_response:
        #(None, None, "안녕하세요 오늘 일정은 ..", None) 토큰은 스트리밍해서 보내되, 히스토리 저장은 다 모였을 때 저장
        if session_id not in SESSION_STORE :
            SESSION_STORE[session_id] = []
        SESSION_STORE[session_id].append(new_massage)
        SESSION_STORE[session_id].append(AIMessage(content=final_response))
        logger.debug((f"[StreamWithStatus] 세션 저장 : {session_id}"))
        
    yield (None, None, final_response, final_tool_name)
    

# SSE 스트리밍 엔드포인트 구현
@router.post("/stream")
async def chat_stream(request:ChatRequest) -> StreamingResponse:
    """SSE 노드 + 토큰 스트리밍 채팅 엔드포인트
    """
    
    logger.info(f"[Stream] 노드 +토큰 스트리밍 요청: session={request.session_id}")
    
    async def generate() -> AsyncGenerator[str,None]:
        # SSE 이벤트 생성기 : 노드 상태 + 토큰 스트리밍
        try :
            async for status, token, final, tool_used in stream_with_status(
                request.message,
                request.session_id,
                request.user_id
            ):
                # 노드 상태 (thinking 이벤트)
                if status:
                    yield StreamEvent(type="thinking", content=status).to_sse()
                    
                if token:
                    yield StreamEvent(type="token", content=token).to_sse()
                    
                if final:
                    yield StreamEvent(type="response", content=final, tool_used=tool_used).to_sse()
                    
            yield StreamEvent(type="done").to_sse()
            logger.info(f"[Stream] 완료: session={request.session_id}")
            
        except Exception as e:
            logger.error(f"[Stream] 오류: {e}")
            yield StreamEvent(type="error", error=str(e)).to_sse()
            yield StreamEvent(type="done").to_sse()
            
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-control" : "no-cache",
            "Connection" : "keep-alive",
            "X-Accel-buffering" : "no"
        }
    )