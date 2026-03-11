# Deployment Guide

이 문서는 `dev` 브랜치의 현재 구성을 기준으로 로컬 실행, Docker 실행, 운영 시 주의할 점을 정리합니다.

## Prerequisites

- Python 3.11+
- `uv`
- Docker / Docker Compose
- Upstage API key
- Supabase 프로젝트
- 선택: Langfuse 프로젝트

## Local Run

의존성 설치:

```bash
uv sync
```

환경 변수 준비:

```bash
cp .env.example .env
```

서버 실행:

```bash
uv run uvicorn app.main:app --reload --reload-dir app --port 8000
```

접속 경로:

- UI: `http://localhost:8000/ui`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health/`

## Docker Run

이미지 빌드:

```bash
docker build -t lumi-agent .
```

컨테이너 실행:

```bash
docker run -p 8000:8000 --env-file .env lumi-agent
```

Compose 실행:

```bash
docker-compose up --build
```

백그라운드 실행:

```bash
docker-compose up -d
```

로그 확인:

```bash
docker-compose logs -f
```

중지:

```bash
docker-compose down
```

## Configuration Notes

### Required in practice

- `UPSTAGE_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Required for PostgreSQL checkpointer

- `ENABLE_CHECKPOINTER=true`
- `CHECKPOINTER_TYPE=postgres`
- `SUPABASE_CONNECTION_STRING`

### Required for Langfuse

- `ENABLE_LANGFUSE=true`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `LANGFUSE_BASE_URL`

## Operational Notes

### Checkpointer

- 기본값은 `postgres`입니다.
- 운영 환경에서는 `memory`보다 `postgres`가 안전합니다.
- 연결 문자열이 없으면 체크포인터 초기화가 실패할 수 있습니다.

### Cost Tracking

- `ENABLE_COST_TRACKING=true`일 때 사용량 추적이 활성화됩니다.
- `DAILY_COST_LIMIT`는 운영 비용 상한을 잡는 용도입니다.
- 알림 연동을 쓰려면 `DISCORD_WEBHOOK_URL`을 채워야 합니다.

### Langfuse

- 앱 시작 시 Langfuse 클라이언트를 초기화합니다.
- 종료 시 flush를 수행하므로, 운영에서는 정상 종료 경로를 보장하는 편이 좋습니다.

## Health Check

Dockerfile과 Compose 모두 헬스 체크에 `/api/v1/health/`를 사용합니다.

수동 확인:

```bash
curl http://localhost:8000/api/v1/health/
```

## Known Gaps

- 현재 `docker-compose.yml`에는 오타와 정리되지 않은 부분이 있을 수 있습니다.
- `.env.example`는 현재 설정 기준으로 맞췄지만, 운영 시 실제 비밀값과 연결 문자열은 별도로 관리해야 합니다.
- 배포 전에는 `uv run pytest`, `uv run ruff check .` 정도는 최소 확인하는 편이 좋습니다.
