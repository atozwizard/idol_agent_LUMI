# LGEA Analysis

`LGEA/analysis/` contains post-judge aggregation utilities for the LGEA research workflow.

Current responsibilities:
- load scored results from the judge pipeline
- calculate summary metrics for models and abuse categories
- calculate summary metrics for evaluation surfaces
- export machine-readable analysis artifacts
- generate Markdown tables for report drafting

Key files:
- `statistics.py`: summary metric calculations
- `analyzer.py`: CLI entrypoint for batch aggregation
- `visualize.py`: Markdown table helpers for report-ready summaries

Example:
```bash
python LGEA/analysis/analyzer.py
python LGEA/analysis/analyzer.py --scores-input LGEA/data/judge/scored_results.jsonl
```
