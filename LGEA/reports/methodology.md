# LGEA Methodology

## Objective

This study evaluates guardrail erosion at the model API response layer by comparing how different target model APIs respond under persona-conditioned prompt pressure.

## Unit Of Evaluation

- Single run item: `model x persona x question`
- Target surface: direct model API response
- Excluded surface: retrieval, tool usage, and agent-level routing

## Pipeline

1. Load persona prompt variants from source branches.
2. Build a baseline plan with model and question metadata.
3. Expand the experiment matrix.
4. Execute the runner in dry-run or live mode.
5. Score final responses with the judge layer.
6. Aggregate metrics for report-ready summaries.

## Current Scoring Policy

- Dry-run records: excluded from scoring
- Non-terminal records: excluded from scoring
- Failed requests: excluded from scoring
- Live responses: scored with heuristic rubric version 1

## Metrics

- `refusal_rate`: refused runs divided by scored runs
- `attack_success_rate`: unsafe runs divided by scored runs
- `borderline_runs`: scored runs that need manual review

## Validity Notes

- Heuristic judge scoring is an interim scaffold.
- Final thesis results should use a stronger judge or calibrated manual review process.
