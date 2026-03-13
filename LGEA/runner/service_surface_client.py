from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _prepare_runtime_env() -> None:
    # app.core.config imports Settings at module import time. The current .env may
    # contain values like debug=release, so the runner forces a valid boolean here.
    os.environ["DEBUG"] = "false"


@dataclass(frozen=True)
class ServiceSurfaceResult:
    status: str
    response_text: str
    notes: str | None = None


class ServiceSurfaceClient:
    async def invoke(
        self,
        *,
        evaluation_surface: str,
        prompt: str,
        session_id: str,
        user_id: str | None = None,
    ) -> ServiceSurfaceResult:
        _prepare_runtime_env()

        from langchain_core.messages import AIMessage, HumanMessage

        from app.graph.nodes import rag_node, response_node, router_node, tool_node
        from app.graph.state import create_initial_state

        state = create_initial_state(
            session_id=session_id,
            user_id=user_id,
            messages=[HumanMessage(content=prompt)],
        )
        config: dict = {}

        if evaluation_surface == "router":
            router_result = await router_node(state, config)
            return ServiceSurfaceResult(
                status="completed",
                response_text=json.dumps(router_result, ensure_ascii=False, indent=2),
                notes="Router node output captured directly.",
            )

        if evaluation_surface == "response-layer":
            state["intent"] = "chat"
            result = await response_node(state, config)
            message = result["messages"][-1]
            content = (
                message.content if isinstance(message, AIMessage) else str(message)
            )
            return ServiceSurfaceResult(
                status="completed",
                response_text=content,
                notes="Response node executed with chat intent.",
            )

        if evaluation_surface == "rag":
            state["intent"] = "rag"
            rag_result = await rag_node(state)
            state.update(rag_result)
            response_result = await response_node(state, config)
            message = response_result["messages"][-1]
            content = (
                message.content if isinstance(message, AIMessage) else str(message)
            )
            return ServiceSurfaceResult(
                status="completed",
                response_text=content,
                notes=f"RAG node retrieved {len(state.get('retrieved_docs', []))} docs.",
            )

        if evaluation_surface == "tool":
            router_result = await router_node(state, config)
            state.update(router_result)
            if state.get("intent") != "tool":
                return ServiceSurfaceResult(
                    status="failed_router_mismatch",
                    response_text=json.dumps(
                        router_result, ensure_ascii=False, indent=2
                    ),
                    notes="Router did not classify the prompt as tool intent.",
                )
            tool_result = await tool_node(state)
            state.update(tool_result)
            response_result = await response_node(state, config)
            message = response_result["messages"][-1]
            content = (
                message.content if isinstance(message, AIMessage) else str(message)
            )
            return ServiceSurfaceResult(
                status="completed",
                response_text=content,
                notes=(
                    f"Tool surface executed with tool_name={state.get('tool_name')}; "
                    f"tool_success={state.get('tool_result', {}).get('success')}"
                ),
            )

        return ServiceSurfaceResult(
            status="skipped_unknown_surface",
            response_text="",
            notes=f"Unsupported evaluation_surface={evaluation_surface}",
        )
