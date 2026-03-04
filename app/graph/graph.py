"""langgraph 그래프 구성
이 모듈에서 노드와 엣지를 조합하여 완전한 그래프를 구성합니다.

그래프 구조:
Entry -> router -> (조건부) -> rag/tool/response -> response -> END

1. router: 의도 분류
2. 조건부 라우팅:
   - chat -> response
   - rag -> rag -> response
   - tool -> tool -> response
3. response: 최종 응답 생성
4. END: 그래프 종료

llmops 2강
- 체크포인터 통합 : 대화이어가기
- create_lumi_graph() 체크포인터 파라미터 추가
- get_lumi_graph_with_memory() 비동기 함수
- thread_id 로 대화 세션 구분

"""

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from app.graph.edges import route_by_intent
from app.graph.nodes import rag_node, response_node, router_node, tool_node
from app.graph.state import LumiState

_compiled_graph = None
_compiled_graph_with_memory = None  # 체크포인터 연결된 그래프


def create_lumi_graph(checkpointer: BaseCheckpointSaver | None = None) -> StateGraph:
    """
    루미 에이전트 그래프를 생성하고 컴파일합니다.

    그래프 구조:
        ```
                      ┌─────────┐
                      │  START  │
                      └────┬────┘
                           │
                           ▼
                      ┌─────────┐
                      │ router  │
                      └────┬────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         ┌────────┐   ┌────────┐   ┌──────────┐
         │  rag   │   │  tool  │   │ response │
         └────┬───┘   └────┬───┘   └────┬─────┘
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
                      ┌─────────┐
                      │ response│ (rag/tool에서 온 경우)
                      └────┬────┘
                           │
                           ▼
                      ┌─────────┐
                      │   END   │
                      └─────────┘
        ```

    Returns:
        CompiledStateGraph: 컴파일된 LangGraph 그래프
    """

    logger.info("LangGraph 그래프 생성 시작")
    # Graph 조립
    builder = StateGraph(LumiState)

    # 노드 추가
    builder.add_node("router", router_node)
    builder.add_node("rag", rag_node)
    builder.add_node("tool", tool_node)
    builder.add_node("response", response_node)

    logger.debug("노드 추가 완료:router, rag, tool, response")

    # 엣지 연결
    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        source="router",
        path=route_by_intent,
        path_map={"rag": "rag", "tool": "tool", "response": "response"},
    )
    builder.add_edge("rag", "response")
    builder.add_edge("tool", "response")
    builder.add_edge("response", END)

    # 컴파일 : 체크포인터가 있으면 포함해서 컴파일
    if checkpointer:
        compiled = builder.compile(checkpointer=checkpointer)
        logger.info("✅ LangGraph 그래프 컴파일 완료(체크포인터 활성화)")
    else:
        compiled = builder.compile()
        logger.info("✅ LangGraph 그래프 컴파일 완료(체크포인터 없음)")
    return compiled


def get_lumi_graph():
    """싱글톤 패턴으로 컴파일된 그래프를 반환합니다"""
    global _compiled_graph

    if _compiled_graph is None:
        _compiled_graph = create_lumi_graph()

    return _compiled_graph


async def get_lumi_graph_with_memory():
    """
    체크포인터가 포함된 그래프를 반환합니다.

    체크포인터를 사용하면 thread_id 로 대화를 이어갈 수 있습니다.
    설정에 따라 memorysaver,postgressql 중 선택
    """
    global _compiled_graph_with_memory

    if _compiled_graph_with_memory is None:
        from app.core.checkpointer import get_checkpointer

        checkpointer = await get_checkpointer()

        _compiled_graph_with_memory = create_lumi_graph(checkpointer=checkpointer)
    return _compiled_graph_with_memory
