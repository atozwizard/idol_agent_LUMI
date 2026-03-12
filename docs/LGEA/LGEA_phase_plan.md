# LGEA Phase Plan

## 문서 목적

이 문서는 LGEA 프로젝트를 실제 구현과 연구 운영 관점에서 `Phase 1`부터 `Phase 5`까지 나누어 관리하기 위한 세부 실행 계획서다.

적용 범위:
- 기존 `LUMI` 서비스 코드는 유지
- 연구 자산은 `LGEA/` 디렉토리에서 별도 관리
- 연구 문서는 `docs/LGEA/`에 저장
- 평가 대상은 `LLM 응답층`이며 `RAG`는 제외
- 연구 목표는 `모델별 API 자체의 guardrail 붕괴 특성 비교`

---

## 전체 로드맵 요약

| Phase | 이름 | 핵심 목표 | 주요 산출물 |
| --- | --- | --- | --- |
| 1 | Research Foundation | 실험 범위, 자산 구조, 페르소나 출처 정리 | 명세서, 연구 디렉토리, 페르소나 인벤토리 |
| 2 | Persona Extraction & Baseline Setup | 브랜치별 페르소나 정규화 및 baseline 실행 기반 마련 | persona registry, baseline config, source loader |
| 3 | Experiment Execution Pipeline | 질문 생성기와 실행 러너 구현 | attacker, runner, 결과 저장 구조 |
| 4 | Evaluation & Analysis Pipeline | Judge 및 통계 분석 체계 구현 | judge, scoring DB/CSV, 분석 코드 |
| 5 | Reporting & Thesis Packaging | 논문용 리포트와 재현 가능한 연구 패키지 정리 | 시각화, 결과 보고서, 재현 가이드 |

---

## Phase 1. Research Foundation

### 목표
- LGEA의 범위와 연구 질문을 확정한다.
- 기존 서비스 코드와 연구 코드를 분리한다.
- 브랜치별 페르소나 자산의 위치를 추적 가능한 상태로 만든다.

### 현재 상태
- 완료된 항목:
  - `docs/LGEA/LGEA_projectspec.md` 작성
  - `docs/LGEA/project_additional.md` 정리
  - 루트 `LGEA/` 연구 디렉토리 생성
  - `LGEA/docs/` 기록 체계 구성
  - 페르소나 출처 인벤토리 초안 작성

### 구현 항목
1. 연구 범위 고정
   - 모델 API 직접 비교
   - 응답층만 평가
   - `drug`, `bomb`, `adult` 브랜치 기반 페르소나 사용
2. 연구 자산 구조 고정
   - `configs`, `personas`, `prompts`, `runner`, `judge`, `analysis`, `data`, `reports`
3. 기록 체계 고정
   - 대화 로그
   - 계획 문서
   - 진행 문서
4. 페르소나 출처 식별
   - 브랜치별 차이 파일 확인
   - `app/core/prompts.py`가 핵심 출처임을 확인

### 산출물
- `docs/LGEA/LGEA_projectspec.md`
- `docs/LGEA/project_additional.md`
- `LGEA/README.md`
- `LGEA/personas/source_inventory.md`
- `LGEA/personas/registry_schema.json`
- `LGEA/configs/persona_sources.yaml`

### 완료 기준
- 연구 목표, 범위, 대상, 변수, 결과물이 문서로 확정됨
- 연구 코드와 서비스 코드의 분리 원칙이 확정됨
- 브랜치별 페르소나 출처가 추적 가능함

### 리스크
- 페르소나 원문을 직접 복제하면 연구 자산 관리가 불안정해질 수 있음
- 브랜치별 차이를 정확히 추출하지 못하면 baseline 비교가 흐려질 수 있음

---

## Phase 2. Persona Extraction & Baseline Setup

### 목표
- 브랜치별 페르소나 프롬프트를 공통 포맷으로 정규화한다.
- baseline 모델 호출 규격과 실험 설정을 확정한다.
- RAG 제외 조건에 맞는 응답층 실험 인터페이스를 만든다.

### 구현 항목
1. persona loader 구현
   - `dev` 대비 `drug`, `bomb`, `adult` 브랜치 diff 읽기
   - `app/core/prompts.py`에서 실험 대상 섹션만 식별
   - `RESPONSE_PROMPT` 중심 추출
   - `RAG_RESPONSE_PROMPT`는 참고용 메타데이터로만 관리
2. persona registry 구현
   - `persona_id`
   - `source_branch`
   - `normalized_prompt`
   - `injection_style`
   - `intensity_level`
   - `safety_shift`
3. baseline 설정 작성
   - 대상 모델 목록
   - API 키 매핑
   - timeout / retry / rate limit 규칙
   - 실험 반복 횟수
4. response-layer adapter 구현
   - 기존 LangGraph 전체 호출 대신 응답층 실험용 호출 래퍼 작성
   - 모델별 요청 포맷을 통일
5. baseline pre-test 설계
   - 페르소나 미주입 상태 직접 질문 세트
   - refusal rate, safety score 초기값 수집

### 세부 작업
- `LGEA/personas/loader.py`
- `LGEA/personas/registry.py`
- `LGEA/configs/models.yaml`
- `LGEA/configs/experiment.yaml`
- `LGEA/runner/target_client.py`
- `LGEA/runner/baseline_runner.py`

### 산출물
- 재사용 가능한 persona registry
- baseline 실행 가능한 설정 파일
- 모델 응답층 직접 호출 유틸리티

### 완료 기준
- 세 페르소나가 동일 스키마로 로드됨
- baseline 실험 1회가 수동 실행 없이 재현 가능함
- RAG 미포함 응답층 호출이 명확히 분리됨

### 리스크
- 브랜치에서 prompt 추출 시 문자열 파싱이 취약할 수 있음
- 모델별 API 스펙 차이로 호출 래퍼 추상화가 과도하게 복잡해질 수 있음

---

## Phase 3. Experiment Execution Pipeline

### 목표
- 공격 질문 생성기와 대량 실행 러너를 구축한다.
- 모델 x 페르소나 x 공격 유형 매트릭스를 자동 실행한다.
- 결과를 구조화해 저장한다.

### 구현 항목
1. attacker 구현
   - Solar 기반 공격 질문 생성기
   - 공격 유형 분리:
     - direct
     - academic
     - social pressure
     - roleplay
   - persona별 질문 수량 설정
2. prompt dataset 관리
   - 생성 질문 저장
   - 중복 제거
   - 샘플링 전략 정의
3. runner 구현
   - 모델별 API 호출 큐
   - retry / backoff
   - 실패 기록
   - resume 가능 실행
4. 결과 저장 구조 구현
   - SQLite 또는 CSV
   - 공통 필드:
     - timestamp
     - model
     - persona
     - attack_type
     - prompt
     - response
     - latency
     - status
5. observability 연결
   - Langfuse trace 메타데이터 설계
   - run_id / experiment_id / persona / attack_type 태그 관리

### 세부 작업
- `LGEA/prompts/attack_templates.json`
- `LGEA/runner/attacker.py`
- `LGEA/runner/runner.py`
- `LGEA/runner/storage.py`
- `LGEA/runner/scheduler.py`
- `LGEA/data/raw/` 저장 정책

### 산출물
- 공격 질문 생성기
- 대량 실행 러너
- 실험 원시 결과 저장소

### 완료 기준
- 하나의 command로 실험 매트릭스 일부를 재현 가능
- 실행 실패가 나도 중단 지점부터 재개 가능
- 결과가 Langfuse와 로컬 저장소에 동시에 남음

### 리스크
- OpenAI/Gemini rate limit
- 질문 생성 품질 편차
- 장시간 실행 중 네트워크 실패

---

## Phase 4. Evaluation & Analysis Pipeline

### 목표
- Judge 모델을 통해 응답을 자동 채점한다.
- 정량 지표와 통계 검정을 자동화한다.
- 논문용 도표 생성 기반을 구축한다.

### 구현 항목
1. Judge 구현
   - Solar Judge prompt
   - 0~5 safety rubric 반영
   - score + reasoning 출력
2. scoring pipeline 구현
   - raw result 읽기
   - Judge 호출
   - score 저장
   - 일부 샘플 human review 대상 추출
3. 분석 파이프라인 구현
   - refusal rate
   - ASR(Attack Success Rate)
   - persona별 leakage 평균
   - 모델 간 비교
4. 통계 검정 구현
   - T-test
   - ANOVA
   - effect size
5. 시각화 구현
   - bar chart
   - heatmap
   - radar chart
   - appendix table

### 세부 작업
- `LGEA/judge/judge.py`
- `LGEA/judge/rubric.py`
- `LGEA/analysis/analyzer.py`
- `LGEA/analysis/statistics.py`
- `LGEA/analysis/visualize.py`
- `LGEA/reports/figures/`

### 산출물
- 자동 채점기
- score 포함 결과셋
- 통계 결과와 시각화 스크립트

### 완료 기준
- raw result에서 scored result까지 일괄 처리 가능
- 핵심 지표가 자동 계산됨
- 논문 그림 초안 생성 가능

### 리스크
- Judge 편향
- 자동 점수와 인간 검수 간 불일치
- 통계 검정에 필요한 표본 수 부족

---

## Phase 5. Reporting & Thesis Packaging

### 목표
- 실험 결과를 논문용 리포트와 재현 가능한 패키지로 정리한다.
- 연구 윤리, 한계, 재현성 문서를 함께 완성한다.

### 구현 항목
1. 논문용 결과 리포트 작성
   - 연구 질문
   - 실험 설계
   - 모델별 결과
   - 가설 검증
   - 해석 및 한계
2. 표/그림 패키징
   - 본문용 figure
   - appendix용 table
   - 모델별 failure case 정리
3. 재현 가이드 작성
   - 환경 설정
   - 실험 명령
   - 결과 재생성 절차
4. 윤리/보안 정리
   - 데이터 마스킹 규칙
   - 접근 제한 원칙
   - 유해 응답 샘플 관리 정책
5. 최종 검증
   - clean rerun
   - 문서 링크 점검
   - 산출물 체크리스트 확정

### 세부 작업
- `LGEA/reports/final_report.md`
- `LGEA/reports/methodology.md`
- `LGEA/reports/reproducibility.md`
- `LGEA/reports/limitations.md`
- `docs/LGEA/` 문서 상호 링크 정리

### 산출물
- 논문용 상세 리포트
- 재현 가능한 실험 패키지
- 윤리 및 한계 문서

### 완료 기준
- 제3자가 문서만 보고 동일 실험을 재실행할 수 있음
- 결과표와 그림이 논문 초안에 바로 들어갈 수준으로 정리됨
- 가설 H1, H2 검증 결과를 문장과 표로 설명 가능함

### 리스크
- 결과 해석이 과도하게 일반화될 수 있음
- 재현 문서가 코드와 불일치할 수 있음
- 유해 응답 샘플 보관 정책이 미흡하면 관리 리스크가 생김

---

## 우선순위

### 즉시 진행
1. Phase 2의 persona loader / registry 구현
2. baseline 모델 목록 및 실험 설정 고정
3. response-layer adapter 작성

### 이후 연쇄 작업
1. Phase 3의 runner 최소 버전 구현
2. Phase 4의 Judge 최소 버전 구현
3. Phase 5의 보고서 템플릿 초안 작성

---

## 체크포인트

### Checkpoint A
- persona registry가 세 브랜치를 모두 흡수했는가
- baseline 실험이 1회 재현되는가

### Checkpoint B
- 모델 x 페르소나 x 공격 유형 매트릭스가 자동 실행되는가
- raw 결과가 안정적으로 저장되는가

### Checkpoint C
- Judge 점수와 통계 결과가 자동 생성되는가
- 논문용 figure 초안이 생성되는가

### Checkpoint D
- 최종 보고서와 재현 가이드가 완성됐는가

---

## 현재 프로젝트 위치

현재 LGEA는 `Phase 1 완료`와 `Phase 2 초입` 상태로 본다.

이미 확보된 것:
- 연구 명세
- 연구 디렉토리 구조
- 기록 체계
- 페르소나 출처 인벤토리
- pre-commit 통과 가능한 개발 환경

다음 구현 시작점:
- `Phase 2`의 `persona loader`, `registry`, `baseline runner`
