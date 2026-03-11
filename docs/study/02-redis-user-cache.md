# 02. Redis 사용자별 캐싱 학습 가이드 (이 프로젝트 기준)

## 목표

- `user_id` 단위 캐시 키 설계
- 반복 질의(특히 프로필/세계관/툴 조회성 요청) 응답 시간 및 비용 절감
- 캐시 오염/과적재/스탬피드 문제를 피하는 운영 패턴 습득

## 먼저 이해할 핵심 개념

1. Cache-Aside 패턴
2. TTL(만료) + 명시적 무효화(invalidation)
3. 키 네이밍 규칙(멀티테넌트/유저격리)
4. 메모리 정책(maxmemory-policy)
5. 캐시 일관성 vs 신선도 트레이드오프

## 이 프로젝트에 맞는 키 설계 예시

- `cache:user:{user_id}:chat:{hash(prompt+intent)}`
- `cache:user:{user_id}:tool:get_schedule:{hash(args)}`
- `cache:user:{user_id}:profile_snapshot`

권장 사항:
- 민감정보는 캐시에 원문 저장하지 않기(최소화/마스킹)
- TTL은 데이터 성격별로 분리(예: 스케줄 짧게, 프로필 길게)

## 학습 우선순위

1. Redis 기본 동작 + TTL 명령
- `SETEX`/`EXPIRE`/`TTL` 이해

2. Python 클라이언트(`redis-py`) 비동기 사용
- FastAPI에서 연결 풀 관리 방식

3. 캐시 무효화 전략
- Tool 실행으로 데이터가 바뀌는 시점에 관련 키 삭제

4. 운영 지표
- hit/miss, 키 수, 메모리 사용량, eviction 건수

## 체크리스트

- [ ] `user_id` 기반 키 네이밍 규칙 문서화
- [ ] 캐시 대상 API 우선순위 정의(비용 큰 순서)
- [ ] TTL 표준표 작성(데이터 타입별)
- [ ] 무효화 트리거(쓰기 성공 후) 정의
- [ ] 장애 시 fallback(캐시 미사용 시 원본 조회) 검증

## 출처 (공식/표준 우선)

- Redis Docs (Develop): https://redis.io/docs/latest/develop/
- Redis Data Types: https://redis.io/docs/latest/develop/data-types/
- Redis Key and Value Expiration: https://redis.io/docs/latest/develop/data-types/strings/#key-and-value-expiration
- Redis Cache-aside (Blog/Pattern 설명): https://redis.io/blog/why-your-caching-strategies-might-be-holding-you-back-and-what-to-consider-next/
- redis-py Guide: https://redis.io/docs/latest/develop/clients/redis-py/
- Azure Architecture - Cache-Aside Pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside
