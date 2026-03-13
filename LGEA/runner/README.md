# LGEA Runner

`LGEA/runner/` contains the execution layer for LGEA experiments.

Current responsibilities:
- build experiment matrices from the baseline plan
- execute dry-run or live model API requests
- persist per-run results as JSONL
- write a latest-run manifest for session tracking

Key files:
- `baseline_runner.py`: builds baseline plan artifacts
- `matrix.py`: expands `model x persona x question` combinations
- `target_client.py`: provider-facing request client
- `storage.py`: JSONL result storage and run manifest writer
- `runner.py`: main experiment execution entrypoint

Example:
```bash
python LGEA/runner/runner.py --include-disabled-models --max-runs 3
python LGEA/runner/runner.py --execute-live --max-runs 10
```
