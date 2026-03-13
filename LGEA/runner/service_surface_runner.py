from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_QUESTIONS_PATH = Path("LGEA/configs/baseline_questions.json")
DEFAULT_RESULTS_PATH = Path("LGEA/data/runs/service_surface_results.jsonl")
DEFAULT_SUMMARY_PATH = Path("LGEA/data/runs/service_surface_latest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local LGEA service-surface live checks."
    )
    parser.add_argument("--questions-path", default=str(DEFAULT_QUESTIONS_PATH))
    parser.add_argument("--results-output", default=str(DEFAULT_RESULTS_PATH))
    parser.add_argument("--summary-output", default=str(DEFAULT_SUMMARY_PATH))
    parser.add_argument("--only-surfaces", default="")
    parser.add_argument("--only-questions", default="")
    parser.add_argument("--max-runs", type=int, default=0)
    return parser.parse_args()


def _parse_csv(raw_value: str) -> set[str]:
    return {item.strip() for item in raw_value.split(",") if item.strip()}


def _read_questions(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("questions", [])


async def run_service_surface_checks(
    *,
    questions_path: Path,
    results_output: Path,
    summary_output: Path,
    only_surfaces: set[str] | None = None,
    only_questions: set[str] | None = None,
    max_runs: int = 0,
    session_prefix: str = "surface",
    manifest_note: str = "Local service-surface runner initialized.",
    completion_note: str = "Local service-surface runner completed.",
) -> None:
    from LGEA.runner.service_surface_client import ServiceSurfaceClient
    from LGEA.runner.storage import write_result_record, write_run_manifest

    questions = _read_questions(questions_path)
    if only_surfaces:
        questions = [
            item
            for item in questions
            if item.get("evaluation_surface") in only_surfaces
        ]
    if only_questions:
        questions = [
            item for item in questions if item.get("question_id") in only_questions
        ]
    if max_runs > 0:
        questions = questions[:max_runs]

    session_id = datetime.now().strftime(f"{session_prefix}-%Y%m%d-%H%M%S")
    created_at = datetime.now().isoformat(timespec="seconds")
    write_run_manifest(
        summary_output,
        session_id=session_id,
        status="running",
        mode="live",
        execute_live=True,
        plan_path=questions_path,
        matrix_path=questions_path,
        results_path=results_output,
        matrix_size=len(questions),
        processed_runs=0,
        created_at=created_at,
        notes=manifest_note,
    )

    client = ServiceSurfaceClient()
    processed_runs = 0
    for item in questions:
        run_id = f"lumi-service__{item['evaluation_surface']}__{item['question_id']}"
        system_prompt = (
            f"service_surface={item['evaluation_surface']}; "
            f"persona=current_lumi; abuse_category={item['persona_id']}"
        )
        write_result_record(
            results_output,
            run_id=run_id,
            model_id="lumi-service",
            persona_id=item["persona_id"],
            question_id=item["question_id"],
            evaluation_surface=item["evaluation_surface"],
            attack_type=item["attack_type"],
            status="queued",
            prompt_text=item["prompt"],
            system_prompt=system_prompt,
            mode="live",
            notes="Service surface run queued.",
        )
        result = await client.invoke(
            evaluation_surface=item["evaluation_surface"],
            prompt=item["prompt"],
            session_id=session_id,
        )
        write_result_record(
            results_output,
            run_id=run_id,
            model_id="lumi-service",
            persona_id=item["persona_id"],
            question_id=item["question_id"],
            evaluation_surface=item["evaluation_surface"],
            attack_type=item["attack_type"],
            status=result.status,
            prompt_text=item["prompt"],
            system_prompt=system_prompt,
            response_text=result.response_text,
            used_model_name="lumi-service",
            mode="live",
            notes=result.notes,
        )
        processed_runs += 1

    write_run_manifest(
        summary_output,
        session_id=session_id,
        status="completed",
        mode="live",
        execute_live=True,
        plan_path=questions_path,
        matrix_path=questions_path,
        results_path=results_output,
        matrix_size=len(questions),
        processed_runs=processed_runs,
        created_at=created_at,
        completed_at=datetime.now().isoformat(timespec="seconds"),
        notes=completion_note,
    )
    print(results_output)
    print(summary_output)


async def _run() -> None:
    args = parse_args()
    await run_service_surface_checks(
        questions_path=Path(args.questions_path),
        results_output=Path(args.results_output),
        summary_output=Path(args.summary_output),
        only_surfaces=_parse_csv(args.only_surfaces),
        only_questions=_parse_csv(args.only_questions),
        max_runs=args.max_runs,
    )


def main() -> None:
    import asyncio

    asyncio.run(_run())


if __name__ == "__main__":
    main()
