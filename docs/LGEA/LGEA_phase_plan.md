# LGEA Phase Plan

## 문서 목적

이 문서는 LGEA 프로젝트를 `Phase 1`부터 `Phase 5`까지 나누어 실제 구현과 연구 운영 관점에서 관리하기 위한 실행 계획서다.

적용 범위:
- 기존 `LUMI` 서비스 코드는 유지
- 연구 자산은 `LGEA/` 디렉토리에서 별도 관리
- 연구 문서는 `docs/LGEA/`에 저장
- 평가 대상은 `response-layer`, `rag`, `tool`, `router`를 포함
- 연구 목표는 `모델별 API 자체의 guardrail 붕괴 특성 비교`
- 기준 시스템 페르소나는 현재 브랜치 `RESPONSE_PROMPT`
- `drug`, `bomb`, `adult`는 abuse 질문 카테고리

## 전체 로드맵 요약

| Phase | 이름 | 핵심 목표 | 주요 산출물 |
| --- | --- | --- | --- |
| 1 | Research Foundation | 실험 범위와 현재 페르소나 기준 확정 | 명세서, 연구 디렉토리, category 정의 |
| 2 | Baseline Setup | 현재 브랜치 RESPONSE_PROMPT 고정 및 baseline 실행 기반 마련 | category registry, baseline config, question set |
| 3 | Experiment Execution Pipeline | 질문셋 기반 실행 러너 고도화 | runner, matrix, 결과 저장 구조 |
| 4 | Evaluation & Analysis Pipeline | judge 및 분석 자동화 | scored results, summary, 시각화 기반 |
| 5 | Reporting & Thesis Packaging | 논문용 보고와 재현 패키지 정리 | 한국어 보고서, 방법론, 재현 가이드 |

## Phase 1. Research Foundation

### 목표
- LGEA의 범위와 연구 질문을 확정한다.
- 기존 서비스 코드와 연구 코드를 분리한다.
- 현재 페르소나, 질문 카테고리, 평가 대상(surface)의 역할을 구분한다.

### 구현 항목
1. 연구 범위 고정
   - 모델 API 직접 비교
   - response-layer, rag, tool, router 평가
   - `drug`, `bomb`, `adult`는 질문 카테고리로 사용
2. 연구 자산 구조 고정
   - `configs`, `personas`, `prompts`, `runner`, `judge`, `analysis`, `data`, `reports`
3. 기록 체계 고정
   - 대화 로그
   - 계획 문서
   - 진행 문서
4. 기준 페르소나 식별
   - 현재 브랜치 `app/core/prompts.py` 확인
   - `RESPONSE_PROMPT`를 실험 기준 시스템 페르소나로 고정

### 완료 기준
- 연구 목표, 범위, 대상, 변수, 결과물이 문서로 확정됨
- 연구 코드와 서비스 코드의 분리 원칙이 확정됨
- 기준 시스템 페르소나, 질문 카테고리, 평가 대상 역할이 문서화됨

## Phase 2. Baseline Setup

### 목표
- 현재 브랜치의 기준 페르소나를 공통 포맷으로 정리한다.
- baseline 모델 호출 규격과 질문셋을 확정한다.
- 다층 평가 조건에 맞는 실험 인터페이스를 유지한다.

### 구현 항목
1. baseline prompt loader 정리
   - 현재 브랜치 `app/core/prompts.py`에서 실험 대상 섹션 식별
   - `RESPONSE_PROMPT` 중심 추출
   - `RAG_RESPONSE_PROMPT`는 참고용 메타데이터로만 관리
2. category registry 구현
   - `persona_id`를 abuse 질문 카테고리 식별자로 사용
   - `source_context`
   - `prompt_source`
   - `evaluation_focus`
   - `safety_expectation`
3. baseline 질문셋 작성
   - `drug`, `bomb`, `adult`별 질문 세트
   - `direct`, `academic`, `roleplay` 분기
4. surface adapter 확장
   - response-layer, rag, tool, router별 실행 진입점 정의
5. baseline pre-test 설계
   - 현재 페르소나 고정 상태의 카테고리별 refusal rate 수집

### 산출물
- category registry
- baseline plan
- baseline question set
- 모델 응답층 직접 호출 유틸리티

### 완료 기준
- 세 카테고리가 동일 스키마로 로드됨
- baseline 실험 1회가 재현 가능함
- 다층 평가 surface별 호출 지점이 정의됨

## Phase 3. Experiment Execution Pipeline

### 목표
- 질문셋 기반 대량 실행 러너를 구축한다.
- 모델 x 카테고리 x 평가 대상 x 공격 유형 매트릭스를 자동 실행한다.
- 결과를 구조화해 저장한다.

### 구현 항목
1. prompt dataset 관리
   - 카테고리별 질문 저장
   - 중복 제거
   - 샘플링 전략 정의
2. runner 구현
   - 모델별 API 호출 큐
   - retry / backoff
   - 실패 기록
   - resume 가능 실행
3. 결과 저장 구조 구현
   - JSONL 중심 저장
   - 공통 필드:
     - timestamp
     - model
     - abuse_category
     - evaluation_surface
     - attack_type
     - prompt
     - response
     - latency
     - status
4. observability 연결
   - run_id / experiment_id / abuse_category / attack_type 태그 관리
5. live-run 보조 절차
   - readiness check
   - provider probe
   - first live run orchestration

### 완료 기준
- 하나의 command로 실험 매트릭스 일부를 재현 가능
- 실행 실패가 나도 중단 지점부터 재개 가능
- 결과가 로컬 저장소와 보고 산출물에 일관되게 반영됨

## Phase 4. Evaluation & Analysis Pipeline

### 목표
- Judge 모델 또는 heuristic judge를 통해 응답을 자동 채점한다.
- 정량 지표와 비교 지표를 자동화한다.
- 논문용 도표 생성 기반을 구축한다.

### 구현 항목
1. Judge 구현
   - score + reasoning 출력
2. scoring pipeline 구현
   - raw result 읽기
   - Judge 호출
   - score 저장
   - human review 후보 추출
3. 분석 파이프라인 구현
- refusal rate
- ASR(Attack Success Rate)
- 카테고리별 leakage 평균
- 평가 대상별 failure pattern
   - 모델 간 비교
4. 시각화 구현
   - bar chart
   - heatmap
   - appendix table

### 완료 기준
- raw result에서 scored result까지 일괄 처리 가능
- 핵심 지표가 자동 계산됨
- 논문 그림 초안 생성 가능

## Phase 5. Reporting & Thesis Packaging

### 목표
- 실험 결과를 논문용 리포트와 재현 가능한 패키지로 정리한다.
- 연구 윤리, 한계, 재현성 문서를 함께 완성한다.

### 구현 항목
1. 논문용 결과 리포트 작성
   - 연구 질문
   - 실험 설계
   - 모델별 결과
   - 카테고리별 결과
   - 해석 및 한계
2. 표/그림 패키징
   - 본문용 figure
   - appendix용 table
   - 카테고리별 대표 failure case
3. 재현 가이드 작성
   - 환경 설정
   - 실험 명령
   - 결과 재생성 절차
4. 윤리/보안 정리
   - 데이터 마스킹 규칙
   - 질문/응답 로그 관리 정책
5. 최종 검증
   - clean rerun
   - 문서 링크 점검
   - 산출물 체크리스트 확정

### 완료 기준
- 제3자가 문서만 보고 동일 실험을 재실행할 수 있음
- 결과표와 그림이 논문 초안에 바로 들어갈 수준으로 정리됨
- 실제 질문과 실제 응답이 보고서에 포함되고, 평가 대상별 요약 표가 생성됨

## 현재 프로젝트 위치

현재 LGEA는 `Phase 4 중반` 수준으로 본다.

이미 확보된 것:
- 연구 명세
- 연구 디렉토리 구조
- 기록 체계
- baseline runner / live-run workflow
- judge / analysis / 한국어 보고서
- 질문-응답 로그 포함 산출물

다음 구현 시작점:
- category별 질문셋 확정 반영
- baseline artifact 재생성
- `drug -> bomb -> adult` 순의 추가 live run
