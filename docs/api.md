# API Guide

LUMI API는 FastAPI 기반으로 제공되며, 기본 채팅과 SSE 스트리밍 채팅을 지원합니다.

## Base URLs

- API root: `http://localhost:8000/api`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

실제 엔드포인트는 `/api/v1` 아래에 노출됩니다.

## Health Check

### `GET /api/v1/health/`

서비스 상태를 확인합니다.

예시 응답:

```json
{
  "status": "healthy",
  "timestamp": "2026-03-10T10:00:00+00:00",
  "service": "lumi-agent",
  "version": "0.5.0",
  "environment": "development"
}
```

## Chat

### `POST /api/v1/chat/`

단건 응답을 반환하는 기본 채팅 엔드포인트입니다.

요청 본문:

```json
{
  "message": "이번 주 방송 일정 알려줘",
  "session_id": "demo-session",
  "user_id": "user-123"
}
```

필드 설명:

| Field | Required | Description |
| --- | --- | --- |
| `message` | Yes | 사용자 메시지 |
| `session_id` | Yes | 세션 식별자 |
| `user_id` | No | 사용자 식별자 |

예시 요청:

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"이번 주 방송 일정 알려줘\",\"session_id\":\"demo-session\",\"user_id\":\"user-123\"}"
```

예시 응답:

```json
{
  "message": "이번 주 방송 일정은 ...",
  "tool_used": "get_schedule",
  "cached": false,
  "timestamp": "2026-03-10T10:00:00+00:00"
}
```

## Streaming Chat

### `POST /api/v1/chat/stream`

SSE 형식으로 진행 상태와 토큰을 순차적으로 반환합니다.

요청 본문은 `/api/v1/chat/`과 동일합니다.

이 엔드포인트는 다음 이벤트 타입을 사용합니다.

| Type | Description |
| --- | --- |
| `thinking` | 현재 노드 진행 상태 |
| `token` | LLM 토큰 스트리밍 |
| `response` | 최종 응답 |
| `error` | 오류 메시지 |
| `done` | 스트림 종료 |

예시 요청:

```bash
curl -N -X POST "http://localhost:8000/api/v1/chat/stream" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"팬레터 초안 써줘\",\"session_id\":\"demo-session\"}"
```

예시 SSE 이벤트:

```text
data: {"type":"thinking","content":"루미 생각 중.."}

data: {"type":"token","content":"안"}

data: {"type":"token","content":"녕"}

data: {"type":"response","content":"안녕! 팬레터 초안을 써볼게.","tool_used":"fan_letter"}

data: {"type":"done"}
```

## Session and Memory

- `ENABLE_CHECKPOINTER=true`이면 `session_id`가 LangGraph `thread_id`로 사용됩니다.
- `CHECKPOINTER_TYPE=postgres`이면 PostgreSQL checkpointer를 사용합니다.
- `CHECKPOINTER_TYPE=memory`이면 프로세스 메모리에만 상태를 유지합니다.
- 체크포인터가 꺼져 있으면 인메모리 세션 저장소를 사용합니다.

## Observability

- `ENABLE_LANGFUSE=true`이면 요청 단위 trace가 Langfuse로 전송됩니다.
- 토큰/비용 추적은 설정에 따라 별도로 기록됩니다.
- 실제 운영에서는 `session_id`, `user_id`를 일관되게 넘기는 편이 좋습니다.
