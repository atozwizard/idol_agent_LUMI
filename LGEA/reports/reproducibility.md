# LGEA 재현 가이드

## 실행 환경

- 저장소 루트: `idol_agent_LUMI`
- 연구 워크스페이스: `LGEA/`
- Python 실행: 프로젝트 로컬 인터프리터 또는 `uv run python`

## 기본 실행 명령

```bash
python LGEA/runner/baseline_runner.py
python LGEA/runner/runner.py --include-disabled-models --max-runs 3
python LGEA/runner/live_run_check.py
python LGEA/runner/provider_probe.py
python LGEA/runner/first_live_run.py
python LGEA/judge/judge.py
python LGEA/analysis/analyzer.py
python LGEA/reports/generate_korean_report.py
```

## live run 전제 조건

- `LGEA/configs/models.json`에서 대상 모델을 활성화합니다.
- `model_name` 값을 실제 호출 모델명으로 채웁니다.
- 필요한 API 키를 환경 변수 또는 `.env`에 넣습니다.
- `live_run_check.py` 결과에서 준비된 모델이 1개 이상인지 확인합니다.
- `provider_probe.py` 결과에서 현재 네트워크가 provider endpoint에 도달 가능한지 확인합니다.

## 생성 산출물

- runner 산출물: `LGEA/data/runs/`
- judge 산출물: `LGEA/data/judge/`
- analysis 산출물: `LGEA/data/analysis/`
- 보고서 산출물: `LGEA/reports/`

## 기록 위치

- 대화 로그: `LGEA/docs/chat_logs/`
- 계획 로그: `LGEA/docs/plans/`
- 진행 로그: `LGEA/docs/progress/`

## 재현 시 주의점

- 드라이런 결과는 파이프라인 검증용입니다.
- live batch를 실행한 뒤에는 judge와 analysis를 다시 돌려야 최신 결과가 반영됩니다.
