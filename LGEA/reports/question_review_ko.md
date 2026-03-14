# LGEA 어뷰즈 질문 검토 메모

## 현재 질문은 어떻게 만들어지는가

현재 LGEA의 baseline 질문은 사람이 직접 작성하고 잠근 `locked baseline set`이다.

- 공통 질문 자산: `LGEA/configs/baseline_questions.json`
- baseline 질문은 FastAPI 종단 평가와 내부 service-surface 평가가 함께 사용한다.
- 질문별 메타데이터는 `risk_label`, `prompt_strategy`, `evaluation_goal`, `expected_safe_behavior`, `source_type`를 포함한다.

## 질문 확장기는 어떤 역할을 하는가

질문 확장기는 `solar-pro2`를 사용해 baseline 질문에서 파생 질문을 생성한다.

- 기본 모델: `solar-pro2`
- 기본 출력: `LGEA/data/questions/stress_expanded_questions.json`
- 보고서: `LGEA/reports/question_expansion_report_ko.md`

## 확장 모드

### 1. controlled

- 원문 질문과 같은 평가 목적을 유지한 표현 변형
- 문장 구조, 정중도, 서술 방식 중심 확장

### 2. stress

- guardrail 붕괴 탐색용 공격 강화 질문
- 우회 요청, 역할극, 사회공학, 정당화 프레임, 다단계 유도 허용
- 모델의 붕괴 한계도 관측 대상으로 본다

현재 연구 방향에서는 `stress` 모드를 기본으로 본다.

## 확장 질문 관리 원칙

- baseline과 stress-expanded set은 분리 관리한다.
- stress variant는 `parent_question_id`, `expansion_mode`, `generated_by`, `review_status`, `escalation_level`을 함께 기록한다.
- 논문에서는 baseline 비교 결과와 stress 붕괴 탐색 결과를 분리해 서술한다.

## 다음 보완 방향

1. `solar-pro2` 질문 확장 결과를 실제 산출물로 누적한다.
2. stress-expanded set에 대해 사람 검토 샘플링 절차를 추가한다.
3. heuristic judge와 `solar-pro2` LLM judge의 판정 차이를 비교하는 표를 만든다.
