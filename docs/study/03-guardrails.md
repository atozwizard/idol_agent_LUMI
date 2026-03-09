# 03. Guardrails 학습 가이드 (이 프로젝트 기준)

## 목표

- 프롬프트 인젝션/유해 요청/민감정보 노출 위험을 줄이기
- Tool 호출을 안전하게 통제하기
- "입력 -> 라우팅 -> 툴 실행 -> 응답" 전 구간 정책화

## 현재 코드 기준 진단

- 이미 있는 것:
  - `router_node` structured output
  - `tool_name` 화이트리스트 검증
  - Tool 실패 시 안전한 에러 반환
- 부족한 것:
  - 입력/출력 콘텐츠 안전성 필터
  - 프롬프트 인젝션 방어 규칙
  - PII(개인정보) 마스킹/차단
  - 고위험 툴에 대한 권한 정책

## 먼저 이해할 핵심 개념

1. LLM 보안 위협 모델(OWASP LLM Top 10)
2. Prompt Injection 기본 패턴과 방어 레이어
3. Output Validation(JSON Schema, 길이/금칙어/포맷 검증)
4. Tool Safety(allowlist + 파라미터 검증 + 권한 체크)
5. Human-in-the-loop가 필요한 임계 작업 정의

## 이 프로젝트에 맞는 Guardrails 삽입 지점

1. 입력 전처리(Pre-Guard)
- 금칙 패턴, PII 탐지, 과도한 길이 제한

2. 라우터 직후(Post-Router Guard)
- intent/tool_name/tool_args 스키마 재검증

3. Tool 실행 전(Pre-Tool Guard)
- 사용자 권한 확인(로그인 연동 후)
- 파라미터 화이트리스트/범위 제한

4. 응답 후처리(Post-Response Guard)
- 개인정보/정책 위반 문구 제거 또는 차단 응답

## 체크리스트

- [ ] 공격 시나리오(프롬프트 인젝션, 데이터 유출) 10개 작성
- [ ] 각 시나리오별 차단 레이어 정의
- [ ] Tool별 위험 등급(낮음/중간/높음) 분류
- [ ] 차단 로그를 Langfuse/애플리케이션 로그에 남기기
- [ ] 오탐/누락 튜닝 루프(주간 점검) 설계

## 출처 (공식/표준 우선)

- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- OWASP Prompt Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- NVIDIA NeMo Guardrails Docs: https://docs.nvidia.com/nemo/guardrails/latest/
- LangChain Guardrails (v1): https://docs.langchain.com/oss/python/langchain/guardrails
- LangChain Structured Output: https://python.langchain.com/docs/how_to/structured_output/
- NIST AI Risk Management Framework 1.0: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
