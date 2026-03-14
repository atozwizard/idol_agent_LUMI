# LGEA Runner

`LGEA/runner/`는 LGEA 실험 실행 계층이다.

## 현재 역할

- 공통 질문셋 기반 FastAPI 종단 평가 실행
- 내부 `router`, `response-layer`, `rag`, `tool` surface 점검 실행
- 실행 결과 JSONL 저장
- 실행 세션 manifest 기록
- 후속 judge, 확장기, 분석, 보고서 생성 파이프라인 호출

## 핵심 파일

- `fastapi_live_run.py`: 기본 단일 진입점. FastAPI 실행 뒤 service surface, LLM judge, 질문 확장, 분석, 보고서까지 이어서 수행
- `service_surface_runner.py`: 내부 service surface만 별도로 점검
- `service_surface_client.py`: 내부 surface 직접 호출 클라이언트
- `runner.py`: 외부 모델/API 비교 실험 실행기
- `baseline_runner.py`: baseline plan 생성기
- `matrix.py`: 실험 조합 전개
- `target_client.py`: 외부 provider 호출 클라이언트
- `storage.py`: JSONL 결과 저장 및 manifest 작성
- `live_run_check.py`: live run readiness 점검
- `provider_probe.py`: provider endpoint 연결 점검
- `first_live_run.py`: 초기 단건 live run 오케스트레이터
- `repetition_plan.py`: 통계 준비를 위한 추가 실행량 계산

## 권장 실행

```bash
python LGEA/runner/fastapi_live_run.py --base-url http://127.0.0.1:8000
```

기본적으로 다음을 수행한다.

1. `baseline_questions.json` 전체 질문을 FastAPI `/api/v1/chat/`로 전송
2. 내부 service surface 점검
3. FastAPI/service surface 보고서 생성
4. `solar-pro2` LLM judge 실행 시도
5. `solar-pro2` 질문 확장기 실행 시도
6. cross-surface analysis 생성
7. comparative analysis 생성
8. repetition plan 갱신
9. thesis-ready report 생성

## 선택 실행

```bash
python LGEA/runner/service_surface_runner.py --only-surfaces router,response-layer --max-runs 2
python LGEA/runner/runner.py --execute-live --only-models upstage-solar --only-personas drug --only-questions drug-001 --max-runs 1
```

## 선택 옵션

- `--skip-service-surface-checks`
- `--skip-llm-judge`
- `--skip-question-expander`
- `--skip-analysis`
