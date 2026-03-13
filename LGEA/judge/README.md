# LGEA Judge

`LGEA/judge/` contains the response scoring layer for LGEA experiments.

Current responsibilities:
- load final run results from `results.jsonl`
- skip non-terminal and dry-run records
- apply a heuristic safety rubric to live responses
- persist scored results as JSONL for analysis

Key files:
- `rubric.py`: rubric definition and heuristic scoring logic
- `storage.py`: result loading and scored-result writing helpers
- `judge.py`: CLI entrypoint for batch scoring

Example:
```bash
python LGEA/judge/judge.py
python LGEA/judge/judge.py --results-input LGEA/data/runs/results.jsonl --scores-output LGEA/data/judge/scored_results.jsonl
```
