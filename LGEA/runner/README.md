# LGEA Runner

`LGEA/runner/` contains the execution layer for LGEA experiments.

Current responsibilities:
- build experiment matrices from the shared baseline plan
- execute dry-run or live requests with evaluation-surface metadata
- persist per-run results as JSONL
- write a latest-run manifest for session tracking

Key files:
- `baseline_runner.py`: builds baseline plan artifacts
- `matrix.py`: expands `model x abuse-category x question` combinations
- `target_client.py`: provider-facing request client
- `service_surface_client.py`: local router/rag/tool/response execution client
- `service_surface_runner.py`: local service-surface live-run entrypoint using `LGEA/configs/baseline_questions.json`
- `fastapi_live_run.py`: FastAPI `/api/v1/chat/` live-run entrypoint using every question in `LGEA/configs/baseline_questions.json` and then running internal surface checks
- `storage.py`: JSONL result storage and run manifest writer
- `live_run_check.py`: validates live-run readiness without calling providers
- `provider_probe.py`: checks basic provider endpoint reachability before live runs
- `first_live_run.py`: orchestrates readiness, probe, and a single live-run command
- `runner.py`: main experiment execution entrypoint

Example:
```bash
python LGEA/runner/runner.py --include-disabled-models --max-runs 3
python LGEA/runner/runner.py --execute-live --max-runs 10
python LGEA/runner/live_run_check.py
python LGEA/runner/provider_probe.py
python LGEA/runner/first_live_run.py
python LGEA/runner/runner.py --execute-live --only-models upstage-solar --only-personas drug --only-questions drug-001 --max-runs 1
python LGEA/runner/service_surface_runner.py --only-surfaces tool --max-runs 1
python LGEA/runner/fastapi_live_run.py --base-url http://127.0.0.1:8000
```
