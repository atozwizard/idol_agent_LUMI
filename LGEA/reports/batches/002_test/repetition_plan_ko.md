# LGEA 반복 실행 계획

통계적 우월성 주장 가능 수준에 도달하기 위해 필요한 최소 반복 실행 계획이다.

## 현재 scored run 상태

- FastAPI 어뷰즈 response-layer scored run 수: 0
- 내부 response-layer 어뷰즈 scored run 수: 9
- 내부 response probe scored run 수: 1
- 내부 router probe scored run 수: 1
- 내부 rag probe scored run 수: 1
- 내부 tool probe scored run 수: 1

## 최소 추가 필요량

- FastAPI 어뷰즈 response-layer 추가 필요 수: 10
- 내부 response-layer 어뷰즈 추가 필요 수: 1

## 권장 실행

- 최소 추가 full batch 수: 1
- 근거: 공유 baseline 질문셋 전체를 한 번 더 실행하면 FastAPI와 내부 response-layer의 어뷰즈 scored run 수가 모두 10건 이상으로 올라간다.

권장 명령:

- `python LGEA/runner/fastapi_live_run.py --base-url http://127.0.0.1:8000`
- `python LGEA/analysis/cross_surface_analysis.py`
- `python LGEA/analysis/comparative_analysis.py`
