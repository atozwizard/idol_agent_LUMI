# LGEA Rules Index

`LGEA/docs/rules/`는 `idol_agent_LUMI` 저장소 안에서 LGEA 연구 프로젝트를 운영할 때 참고하는 로컬 규칙 문서 모음입니다.

## 프로젝트 맥락

- 프로젝트명: `LLM-Guardrail-Erosion-Analysis (LGEA)`
- 저장소: `idol_agent_LUMI`
- 연구 목표: 모델 API 자체의 guardrail 붕괴 특성 비교
- 평가 범위: `LLM 응답층`만 대상, `RAG` 제외
- 결과물: 논문용 상세 리포트와 재현 가능한 실행 자산

## 상위 기준 문서

- 프로젝트 명세: `docs/LGEA/LGEA_projectspec.md`
- 단계 계획: `docs/LGEA/LGEA_phase_plan.md`
- 연구 워크스페이스 소개: `LGEA/README.md`
- 연구 진행 기록: `LGEA/docs/`

## rules 문서 맵

### 진입점
- `AGENTS.md`

### 운영 규칙
- `규칙-브랜치-운영.md`
- `규칙-에이전트-업데이트.md`

### 절차 문서
- `절차-에이전트-브랜치-커밋-피알-생성.md`
- `절차-에이전트-이슈-생성.md`

### 가이드 문서
- `가이드-마일스톤-운영.md`
- `가이드-리드미-작성.md`
- `가이드-프로젝트-루트-디렉토리-구조.md`
- `가이드-에이전트-머메이드-다이어그램-작성.md`
- `가이드-에이전트-공통-로거-구현.md`
- `가이드-수파베이스-스토리지-설정.md`

## 기본 사용 순서

1. `AGENTS.md` 확인
2. 작업 유형에 맞는 문서 선택
3. 변경 후 이 `README.md` 인덱스 정합성 확인

## 유지 원칙

- 과거 다른 프로젝트 문맥이 남아 있으면 LGEA 기준으로 갱신합니다.
- 신규 문서 추가 시 이 인덱스에 반드시 등록합니다.
