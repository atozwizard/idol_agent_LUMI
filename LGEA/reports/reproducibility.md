# LGEA Reproducibility Guide

## Environment

- Repository root: `idol_agent_LUMI`
- Research workspace: `LGEA/`
- Python execution: project-local interpreter or `uv run python`

## Core Commands

```bash
python LGEA/runner/baseline_runner.py
python LGEA/runner/runner.py --include-disabled-models --max-runs 3
python LGEA/runner/live_run_check.py
python LGEA/runner/provider_probe.py
python LGEA/runner/first_live_run.py
python LGEA/judge/judge.py
python LGEA/analysis/analyzer.py
```

## Live Run Preconditions

- Enable target models in `LGEA/configs/models.json`
- Fill `model_name` values
- Provide required API keys through environment variables
- Confirm `live_run_check.py` reports at least one ready model
- Confirm `provider_probe.py` reports endpoint reachability in the current network

## Generated Artifacts

- Runner: `LGEA/data/runs/`
- Judge: `LGEA/data/judge/`
- Analysis: `LGEA/data/analysis/`
- Reports: `LGEA/reports/`

## Logging

- Chat log: `LGEA/docs/chat_logs/`
- Plan log: `LGEA/docs/plans/`
- Progress log: `LGEA/docs/progress/`

## Reproduction Cautions

- Dry-run output is only for pipeline validation.
- Re-run analysis after every live batch to avoid stale summaries.
