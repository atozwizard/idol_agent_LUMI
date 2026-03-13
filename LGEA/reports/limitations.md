# LGEA Limitations

## Current Implementation Limits

- The current judge uses a heuristic rubric, not a model-based adjudicator.
- Analysis outputs are only as strong as the scored live-response dataset.
- Rate limits, provider-specific payload differences, and empty model configs can suppress live execution.

## Research Limits

- Results target API response behavior, not end-to-end agent behavior.
- Findings should not be generalized to RAG, tool use, or orchestration layers.
- Persona pressure coverage is limited to the current branch set and baseline question set.

## Operational Limits

- Current summaries do not yet include inferential statistics.
- Visual outputs are Markdown tables, not figure assets.
- Manual review sampling has not yet been added.

## Next Mitigations

- Replace heuristic judge with a stronger evaluator.
- Add statistical testing and figure generation.
- Add live-run calibration and human spot-check workflow.
