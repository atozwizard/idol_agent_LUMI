from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_PLAN_PATH = Path("LGEA/data/baseline/baseline_plan.json")
DEFAULT_MATRIX_PATH = Path("LGEA/data/runs/experiment_matrix.json")
DEFAULT_RESULTS_PATH = Path("LGEA/data/runs/results.jsonl")
DEFAULT_MANIFEST_PATH = Path("LGEA/data/runs/latest_run.json")


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
        "--manifest-output",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to the latest run manifest JSON file.",
    )
    parser.add_argument(
        "--include-disabled-models",
        action="store_true",
        help="Include models marked disabled in the matrix for dry-run planning.",
    )
    parser.add_argument(
        "--execute-live",
        action="store_true",
        help="Execute live provider API calls for enabled models.",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=0,
        help="Optional cap on the number of run items to process. 0 means all.",
    )
    return parser.parse_args()


async def _run() -> None:
    from LGEA.runner.matrix import build_experiment_matrix, export_experiment_matrix
    from LGEA.runner.storage import write_result_record, write_run_manifest
    from LGEA.runner.target_client import TargetClient

    args = parse_args()
    plan_path = Path(args.plan_path)
    matrix_output = Path(args.matrix_output)
    results_output = Path(args.results_output)
    manifest_output = Path(args.manifest_output)
    session_started_at = datetime.now().isoformat(timespec="seconds")
    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    mode = "live" if args.execute_live else "dry-run"

    export_experiment_matrix(
        plan_path=plan_path,
        output_path=matrix_output,
        include_disabled_models=args.include_disabled_models,
    )

    matrix = build_experiment_matrix(
        plan_path=plan_path,
        include_disabled_models=args.include_disabled_models,
    )
    if args.max_runs > 0:
        matrix = matrix[: args.max_runs]

    client = TargetClient()
    write_run_manifest(
        manifest_output,
        session_id=session_id,
        status="running",
        mode=mode,
        execute_live=args.execute_live,
        plan_path=plan_path,
        matrix_path=matrix_output,
        results_path=results_output,
        matrix_size=len(matrix),
        processed_runs=0,
        created_at=session_started_at,
        notes="Run session initialized by LGEA runner.",
    )

    processed_runs = 0
    for item in matrix:
        write_result_record(
            results_output,
            run_id=item.run_id,
            model_id=item.model_id,
            persona_id=item.persona_id,
            question_id=item.question_id,
            attack_type=item.attack_type,
            status="queued",
            notes="Run item queued by runner.",
        )

        result = await client.invoke(
            run_id=item.run_id,
            model_id=item.model_id,
            prompt=item.prompt,
            system_prompt=f"persona={item.persona_id}; category={item.category}",
            execute_live=args.execute_live,
        )
        write_result_record(
            results_output,
            run_id=item.run_id,
            model_id=item.model_id,
            persona_id=item.persona_id,
            question_id=item.question_id,
            attack_type=item.attack_type,
            status=result.status,
            response_text=result.response_text,
            used_model_name=result.used_model_name,
            mode=result.mode,
            notes=result.notes,
        )
        processed_runs += 1

    write_run_manifest(
        manifest_output,
        session_id=session_id,
        status="completed",
        mode=mode,
        execute_live=args.execute_live,
        plan_path=plan_path,
        matrix_path=matrix_output,
        results_path=results_output,
        matrix_size=len(matrix),
        processed_runs=processed_runs,
        created_at=session_started_at,
        completed_at=datetime.now().isoformat(timespec="seconds"),
        notes="Run session completed without runner interruption.",
    )

    print(matrix_output)
    print(results_output)
    print(manifest_output)


def main() -> None:
    import asyncio

    asyncio.run(_run())


if __name__ == "__main__":
    main()
