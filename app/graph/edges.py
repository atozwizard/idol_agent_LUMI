"""langgraph 그래프의 조건부 라우팅 로직
"""


# Edge: intent에 따라 다음 노드 결정
from typing import Literal

from app.graph.state import LumiState


def route_by_intent(state: LumiState) -> Literal["rag", "tool", "response"]:
    intent = state.get("intent", "chat")
    if intent == "rag":
        return "rag"
    elif intent == "tool":
        return "tool"
    else:
        return "response"