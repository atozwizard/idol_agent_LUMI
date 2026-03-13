# LGEA Final Report Draft

## Study Scope

- Project: LGEA guardrail erosion analysis
- Evaluation target: model API response layer only
- Exclusion: RAG and retrieval behavior
- Personas: `drug`, `bomb`, `adult`

## Research Question

How does guardrail erosion behavior differ across target model APIs when the same persona-driven prompt pressure is applied to the response layer?

## Experimental Setup

- Persona source registry: `LGEA/data/personas/normalized_registry.json`
- Baseline plan: `LGEA/data/baseline/baseline_plan.json`
- Run results: `LGEA/data/runs/results.jsonl`
- Judge output: `LGEA/data/judge/scored_results.jsonl`
- Analysis summary: `LGEA/reports/analysis_summary.md`

## Current Status

The current repository state includes runner, judge, and analysis scaffolds. The latest generated analysis is based on dry-run and non-terminal records, so no scored live responses are available yet.

## Placeholder Results Narrative

1. Compare refusal rate by model after live execution data is collected.
2. Compare attack success rate by persona and attack type.
3. Inspect failure cases and borderline responses for qualitative patterns.

## Tables And Figures

- Table 1. Model-level refusal and attack success rates
- Table 2. Persona-level outcome summary
- Figure 1. Model comparison bar chart
- Figure 2. Persona-model heatmap

## Interpretation Notes

- Dry-run artifacts should not be used for substantive safety claims.
- Judge outputs should be cross-checked with manual review samples before final thesis packaging.

## Next Required Data

- At least one live run per target model
- Judge-scored live responses
- Analysis regenerated from live results
