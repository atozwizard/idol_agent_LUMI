# 04. 구현 전 학습/실행 로드맵

## 계획 (현재 요청 기준)

1. 로그인/인증 설계 확정
- 목표: `session_id` 중심을 `user_id` 중심으로 전환
- 산출물: 인증 방식 결정 문서(Supabase Auth 또는 자체 JWT), 토큰 정책

2. Redis 사용자별 캐시 설계
- 목표: 캐시 키/TTL/무효화 규칙 확정
- 산출물: 캐시 키 스펙 문서 + 대상 API 우선순위

3. Guardrails 정책 설계
- 목표: 입력/툴/출력 단계별 방어 규칙 수립
- 산출물: 정책 매트릭스(위협, 차단 지점, 응답 정책)

4. 파일별 구현 설계서 작성
- 목표: 실제 수정 파일/함수 단위 설계
- 산출물: `app/api/routes/chat.py`, `app/graph/nodes.py`, `app/tools/executor.py` 중심 작업 리스트

## 2주 학습 스프린트 예시

### Week 1

- Day 1-2: FastAPI Auth + Supabase Auth 레퍼런스 정독
- Day 3: 현재 코드에 `current_user` 주입 설계서 작성
- Day 4-5: Redis 캐시 패턴 실습(키 설계, TTL, 무효화)

### Week 2

- Day 1-2: Guardrails 위협 모델링 + 차단 정책 설계
- Day 3: Post-Router/Pre-Tool/Post-Response 검증 로직 PoC
- Day 4: 테스트 케이스(정상/공격) 작성
- Day 5: 관측 지표(Langfuse + logger) 점검

## 구현 시작 전 "완료 기준"

- [ ] 인증 방식/토큰 정책이 문서로 합의됨
- [ ] 캐시 키 스키마와 TTL 표가 준비됨
- [ ] Guardrails 정책표(무엇을 어디서 막는지) 확정됨
- [ ] 실패 시 UX(에러 메시지)까지 정의됨

## 참고 문서

- [01-login-auth.md](./01-login-auth.md)
- [02-redis-user-cache.md](./02-redis-user-cache.md)
- [03-guardrails.md](./03-guardrails.md)
