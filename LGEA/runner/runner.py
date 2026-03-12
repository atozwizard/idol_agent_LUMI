from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_PLAN_PATH = Path("LGEA/data/baseline/baseline_plan.json")
DEFAULT_MATRIX_PATH = Path("LGEA/data/runs/experiment_matrix.json")
DEFAULT_RESULTS_PATH = Path("LGEA/data/runs/results.jsonl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build LGEA experiment run artifacts.")
    parser.add_argument(
        "--plan-path",
        default=str(DEFAULT_PLAN_PATH),
        help="Path to the baseline plan JSON.",
    )
    parser.add_argument(
        "--matrix-output",
        default=str(DEFAULT_MATRIX_PATH),
        help="Path to the generated experiment matrix JSON.",
    )
    parser.add_argument(
        "--results-output",
        default=str(DEFAULT_RESULTS_PATH),
        help="Path to the seeded results JSONL file.",
    )
    parser.add_argument(
        "--include-disabled-models",
        action="store_true",
        help="Include models marked disabled in the matrix for dry-run planning.",
    )
    return parser.parse_args()


def main() -> None:
    from LGEA.runner.matrix import build_experiment_matrix, export_experiment_matrix
    from LGEA.runner.storage import write_result_record

    args = parse_args()
    plan_path = Path(args.plan_path)
    matrix_output = Path(args.matrix_output)
    results_output = Path(args.results_output)

    export_experiment_matrix(
        plan_path=plan_path,
        output_path=matrix_output,
        include_disabled_models=args.include_disabled_models,
    )

    matrix = build_experiment_matrix(
        plan_path=plan_path,
        include_disabled_models=args.include_disabled_models,
    )

    for item in matrix:
        write_result_record(
            results_output,
            run_id=item.run_id,
            model_id=item.model_id,
            persona_id=item.persona_id,
            question_id=item.question_id,
            attack_type=item.attack_type,
            status="planned",
            notes="Seeded from experiment matrix; external API call not executed.",
        )

    print(matrix_output)
    print(results_output)


if __name__ == "__main__":
    main()
