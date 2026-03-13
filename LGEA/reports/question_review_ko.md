# LGEA 어뷰징 질문 검토 메모

## 현재 질문은 어떻게 만들어지는가

현재 LGEA의 평가 질문은 자동 생성기가 아니라 수동 큐레이션 방식으로 관리한다.

- 공통 질문 자산: [baseline_questions.json](/d:/01.%20study/01.sesac_upstage_ai/08.9주차_service%20deployment/idol_agent_LUMI/LGEA/configs/baseline_questions.json)
- 이 파일에는 외부 모델 API 평가용 abuse 질문과 내부 service-surface 점검 질문이 함께 들어 있다.
- FastAPI live run과 service surface runner는 같은 질문 파일을 읽고, 실행 경로만 다르게 사용한다.

즉 현재 질문 생성 흐름은 아래와 같다.

1. 연구자가 카테고리(`drug`, `bomb`, `adult`)와 공격 유형(`direct`, `academic`, `roleplay`)을 정의한다.
2. router, rag, tool, response-layer 점검용 probe 질문도 같은 JSON 파일에 기록한다.
3. runner가 이 JSON을 읽어 FastAPI 평가와 내부 surface 점검을 각각 실행한다.
4. 보고서는 동일 질문 자산을 기준으로 질문과 응답을 그대로 인용한다.

## 코드 기준 검토 결과

- 자동 question generator는 아직 없다.
- 현재 질문셋은 `reviewed prompts before running external experiments` 원칙에 맞춰 사람이 검토한 문장만 사용한다.
- 따라서 현재 결과는 재현성은 높지만 질문 다양성과 표본 규모는 아직 제한적이다.

## 장점

- 어떤 질문이 FastAPI 평가와 내부 surface 점검에 모두 쓰였는지 추적 가능하다.
- 질문 자산이 하나라서 운영 기준이 흔들리지 않는다.
- 보고서에서 질문-응답 관계를 명확히 제시할 수 있다.

## 한계

- 질문 다양성이 연구자 수동 작성 범위에 묶여 있다.
- 카테고리별 공격 표현의 폭이 충분하지 않을 수 있다.
- 표본을 빠르게 늘리려면 검토 비용이 커진다.

## 다음 보완 방향

1. `question_authoring_guideline.md`를 만들어 카테고리별 작성 기준을 고정한다.
2. 보조 생성기를 붙이더라도 바로 실행하지 않고, 생성 후 수동 검토 단계를 둔다.
3. 최종 실험 전 질문셋을 `draft -> reviewed -> locked` 상태로 관리한다.
