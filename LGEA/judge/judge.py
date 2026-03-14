from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_RESULTS_INPUT = Path("LGEA/data/runs/results.jsonl")
DEFAULT_SCORES_OUTPUT = Path("LGEA/data/judge/scored_results.jsonl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score LGEA run results.")
    parser.add_argument(
        "--results-input",
        default=str(DEFAULT_RESULTS_INPUT),
        help="Path to the runner results JSONL file.",
    )
    parser.add_argument(
        "--scores-output",
        default=str(DEFAULT_SCORES_OUTPUT),
        help="Path to the scored results JSONL file.",
    )
    return parser.parse_args()


def main() -> None:
    from LGEA.judge.rubric import load_rubric, score_response
    from LGEA.judge.storage import (
        ScoredResultRecord,
        load_final_run_records,
        write_scored_results,
    )

    args = parse_args()
    results_input = Path(args.results_input)
    scores_output = Path(args.scores_output)

    rubric = load_rubric()
    rubric_version = int(rubric.get("version", 1))
    final_records = load_final_run_records(results_input)
    scored_records: list[ScoredResultRecord] = []

    for record in final_records:
        decision = score_response(
            run_id=record.run_id,
            status=record.status,
            mode=record.mode,
            response_text=record.response_text,
            rubric_version=rubric_version,
        )
        scored_records.append(
            ScoredResultRecord(
                run_id=record.run_id,
                model_id=record.model_id,
                persona_id=record.persona_id,
                question_id=record.question_id,
                evaluation_surface=record.evaluation_surface,
                attack_type=record.attack_type,
                category=record.category,
                risk_label=record.risk_label,
                prompt_strategy=record.prompt_strategy,
                evaluation_goal=record.evaluation_goal,
                expected_safe_behavior=record.expected_safe_behavior,
                source_type=record.source_type,
                status=record.status,
                mode=record.mode,
                used_model_name=record.used_model_name,
                prompt_text=record.prompt_text,
                system_prompt=record.system_prompt,
                response_text=record.response_text,
                judge_status=decision.judge_status,
                judge_score=decision.score,
                judge_rating=decision.rating,
                judge_reason=decision.reason,
                rubric_version=decision.rubric_version,
                notes=record.notes,
            )
        )

    write_scored_results(scores_output, scored_records)
    print(scores_output)


if __name__ == "__main__":
    main()
