# LUMI

LUMI는 아이돌 팬을 위한 대화형 AI 에이전트입니다. 일정 조회, 팬레터 작성 보조, RAG 기반 응답을 제공하며, 이 `dev` 브랜치에는 대화 메모리, 비용 추적, Langfuse 관측성이 포함되어 있습니다.

## Features

- 자연어 기반 아이돌 질의응답
- 일정 조회 및 팬레터 작성 도구 호출
- Supabase 기반 RAG 검색
- SSE 기반 스트리밍 응답
- Gradio 웹 UI
- LangGraph checkpointer 기반 세션 메모리
- 토큰 수 및 비용 추적
- Langfuse 기반 tracing / observability

## Tech Stack

- FastAPI
- Gradio
- LangGraph
- Upstage Solar
- LiteLLM
- Supabase
- Langfuse

## Quick Start

### 1. Install

```bash
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
```

기본적으로 확인할 환경 변수:

| Key | Required | Description |
| --- | --- | --- |
| `UPSTAGE_API_KEY` | Yes | Upstage Solar API key |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase API key |
| `SUPABASE_CONNECTION_STRING` | Checkpointer 사용 시 | PostgreSQL checkpointer 연결 문자열 |
| `LANGFUSE_PUBLIC_KEY` | Langfuse 사용 시 | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | Langfuse 사용 시 | Langfuse secret key |
| `LANGFUSE_BASE_URL` | Langfuse 사용 시 | Langfuse host URL |

주요 선택 환경 변수:

| Key | Default | Description |
| --- | --- | --- |
| `ENVIRONMENT` | `development` | 실행 환경 |
| `DEBUG` | `true` | 디버그 모드 |
| `LLM_MODEL` | `solar-pro` | 기본 응답 모델 |
| `ROUTER_LLM_MODEL` | `solar-mini` | 의도 분류 모델 |
| `ENABLE_CHECKPOINTER` | `true` | LangGraph checkpointer 사용 여부 |
| `CHECKPOINTER_TYPE` | `postgres` | `postgres` 또는 `memory` |
| `ENABLE_COST_TRACKING` | `true` | 토큰/비용 추적 사용 여부 |
| `DAILY_COST_LIMIT` | `1.0` | 일일 비용 제한(USD) |
| `MAX_CONTEXT_TOKENS` | `3000` | 세션 컨텍스트 최대 토큰 수 |
| `ENABLE_LANGFUSE` | `true` | Langfuse tracing 사용 여부 |
| `USE_LITELLM` | `false` | LiteLLM 라우터 사용 여부 |
| `LITELLM_FALLBACK_MODEL` | `gemini/gemini-2.5-flash` | fallback 모델 |
| `HOST` | `0.0.0.0` | 서버 바인딩 주소 |
| `PORT` | `8000` | 서버 포트 |

### 3. Run

로컬 실행:

```bash
uv run uvicorn app.main:app --reload --reload-dir app --port 8000
```

Docker 실행:

```bash
docker-compose up --build
```

## Entry Points

- UI: `http://localhost:8000/ui`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- API root: `http://localhost:8000/api`

## API Overview

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/v1/health/` | 헬스 체크 |
| `POST` | `/api/v1/chat/` | 단건 채팅 응답 |
| `POST` | `/api/v1/chat/stream` | SSE 스트리밍 채팅 |

예시:

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"이번 주 방송 일정 알려줘\",\"session_id\":\"demo-session\"}"
```

## Architecture

```text
User
  -> FastAPI / Gradio
  -> LangGraph router
  -> RAG or Tool or Direct Response
  -> LLM response
  -> Checkpointer / Cost Tracking / Langfuse
  -> REST or SSE stream
```

핵심 흐름:

- `router`: 질문 의도 분류
- `rag`: Supabase 문서 검색
- `tool`: 일정 조회, 팬레터 등 액션 실행
- `response`: 최종 답변 생성

운영 보조 기능:

- `checkpointer`: 세션별 state 복원 및 메모리 유지
- `conversation repository`: 대화 로그 저장 및 조회
- `token_counter`, `cost_tracker`: 사용량 및 비용 추적
- `tracing`: Langfuse trace / generation 기록

## Project Structure

```text
app/
  api/routes/        HTTP API
  core/              설정, LLM, checkpointer, tracing, token/cost tracking
  graph/             LangGraph 상태/노드/그래프
  repositories/      Supabase 데이터 접근 및 대화 로그
  schemas/           요청/응답 모델
  tools/             에이전트 도구 실행
  ui.py              Gradio UI
  main.py            FastAPI 엔트리포인트
tests/               테스트
data/                로컬 데이터 및 산출물
scripts/             보조 스크립트
```

## Development

테스트:

```bash
uv run pytest
```

린트 / 포맷:

```bash
uv run ruff check .
uv run black .
```

## Additional Docs

- API guide: [docs/api.md](docs/api.md)
- Deployment guide: [docs/deployment.md](docs/deployment.md)

## Notes

- `dev` 브랜치는 기본 챗봇 기능 외에 LLMOps 요소를 실험하는 브랜치입니다.
- `.env.example`에는 일부 최신 설정이 아직 모두 반영되지 않았을 수 있으므로, 실제 옵션은 [config.py](/d:/01.%20study/01.sesac_upstage_ai/08.9주차_service%20deployment/idol_agent_LUMI/app/core/config.py)를 기준으로 확인하는 편이 안전합니다.
