# Study Guide: 로그인 + Redis 사용자별 캐싱 + Guardrails

이 문서는 현재 `idol_agent_LUMI` 프로젝트(FastAPI + LangGraph + Supabase) 기준으로,
다음 3가지를 구현하기 전에 무엇을 공부해야 하는지 정리한 인덱스다.

- 로그인/인증(Authorization 포함)
- Redis 기반 사용자별 캐싱
- LLM Guardrails

## 추천 학습 순서

1. [01-login-auth.md](./01-login-auth.md)
2. [02-redis-user-cache.md](./02-redis-user-cache.md)
3. [03-guardrails.md](./03-guardrails.md)
4. [04-implementation-roadmap.md](./04-implementation-roadmap.md)

## 왜 이 순서인가

- 로그인 설계가 먼저 고정되어야 사용자 식별자(`user_id`)가 안정화됨
- 사용자 식별자가 있어야 Redis 캐시 키 설계를 안전하게 할 수 있음
- Guardrails는 인증/캐싱 이후 전체 요청 파이프라인에 걸쳐 삽입해야 운영이 쉬움
