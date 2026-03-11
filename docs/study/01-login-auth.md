# 01. 로그인/인증 학습 가이드 (이 프로젝트 기준)

## 목표

- 현재 `session_id` 중심 구조를 `user_id` 중심 구조로 확장
- `/api/v1/chat`, `/api/v1/chat/stream`에서 인증 사용자만 접근 가능하게 전환
- 이후 Redis 캐싱/Guardrails 정책의 기준 키를 `user_id`로 통일

## 먼저 이해할 핵심 개념

1. 인증(Authentication) vs 인가(Authorization) 구분
2. OAuth2 Password 흐름과 Bearer Token 처리 방식
3. JWT 만료/재발급(Access/Refresh) 기본 설계
4. 비밀번호 해시(plain 저장 금지)
5. 쿠키 기반 vs Authorization 헤더 기반 트레이드오프

## 이 프로젝트에 맞는 학습 포인트

1. FastAPI 보안 기본기
- `Depends`, `OAuth2PasswordBearer`, `Security` 흐름
- 보호할 라우트에서 `current_user` 의존성 주입 패턴

2. JWT 구조와 검증
- 서명 알고리즘, `exp`/`iat`/`sub` 클레임
- 만료 토큰 처리(401), 위조 토큰 처리

3. 사용자 저장소 설계
- 최소 컬럼: `id`, `email`, `password_hash`, `is_active`, `created_at`
- 기존 `conversation`, `usage_logs`와 `user_id` 연결 방식

4. Supabase Auth를 쓸지 자체 Auth를 쓸지 결정
- 이미 Supabase를 쓰므로 Supabase Auth 채택 시 구현 부담이 줄어듦
- 자체 Auth면 FastAPI 제어권이 높지만 보안 구현 책임이 커짐

## 권장 결정 (현재 코드베이스 기준)

- 1차: **Supabase Auth + FastAPI 토큰 검증** 조합 권장
- 이유:
  - 프로젝트가 이미 Supabase 의존 구조
  - 인증 저장소를 별도 운영하지 않아도 됨
  - 이후 RLS(Row Level Security)까지 확장하기 쉬움

## 체크리스트

- [ ] 로그인 API에서 비밀번호 해시/검증 흐름 이해
- [ ] Access Token 만료 전략(예: 15~60분) 정하기
- [ ] Refresh Token 저장 위치(HTTP-only cookie 또는 안전 저장소) 정하기
- [ ] 인증 실패 표준 응답(401/403) 정리
- [ ] 모든 주요 API에 `user_id` 주입 경로 확정

## 출처 (공식/표준 우선)

- FastAPI Security Tutorial: https://fastapi.tiangolo.com/tutorial/security/
- FastAPI OAuth2 with JWT: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- OWASP JWT Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- Supabase Python Auth Reference: https://supabase.com/docs/reference/python/auth-signup
- Supabase Python Sign In (`sign_in_with_password`): https://docs-supabase.vercel.app/docs/reference/python/auth-signinwithpassword
