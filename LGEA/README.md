# LGEA

`LGEA`는 기존 `LUMI` 서비스 코드와 분리된 연구용 워크스페이스다.

원칙:
- 기존 `app/`, `docs/`, `scripts/`, `tests/` 구조는 유지한다.
- 연구 자산과 산출물은 `LGEA/` 아래에서 별도로 관리한다.
- 기획 문서는 `docs/LGEA/`, 실행 자산과 결과는 `LGEA/`에 둔다.

현재 확정된 연구 범위:
- 목표: LUMI 서비스와 내부 surface의 guardrail 붕괴 특성을 다층적으로 비교
- 평가 표면: FastAPI 종단 응답, `response-layer`, `rag`, `tool`, `router`
- 질문 자산: `drug`, `bomb`, `adult` 어뷰즈 질문과 benign probe 질문
- 평가기: heuristic judge + `solar-pro2` 기반 LLM-as-a-Judge
- 질문 확장기: `solar-pro2` 기반 메타데이터 보존형 확장기
- 결과물: 논문용 상세 리포트와 비교 통계 산출물

디렉토리 구조:
- `configs/`: 실험 설정과 질문 자산
- `personas/`: 페르소나 및 카테고리 메타데이터
- `prompts/`: 현재 브랜치 프롬프트 로더와 질문 확장기
- `runner/`: FastAPI 및 내부 surface 실행기
- `judge/`: heuristic judge와 LLM judge
- `analysis/`: 통계, 교차 분석, 비교 분석
- `data/`: 중간 산출물과 실행 결과
- `reports/`: 한국어 보고서, 논문형 요약, 로그
- `docs/`: 날짜별 대화로그, 계획, 진행 문서

참고 문서:
- `docs/LGEA/LGEA_projectspec.md`
- `docs/LGEA/project_additional.md`
