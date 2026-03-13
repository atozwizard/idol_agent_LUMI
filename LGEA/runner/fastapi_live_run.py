from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

import httpx

from LGEA.runner.service_surface_runner import run_service_surface_checks
from LGEA.runner.storage import write_result_record, write_run_manifest

DEFAULT_QUESTIONS_PATH = Path("LGEA/configs/baseline_questions.json")
DEFAULT_RESULTS_PATH = Path("LGEA/data/runs/fastapi_live_results.jsonl")
DEFAULT_SUMMARY_PATH = Path("LGEA/data/runs/fastapi_live_latest.json")
DEFAULT_SERVICE_RESULTS_PATH = Path("LGEA/data/runs/service_surface_results.jsonl")
DEFAULT_SERVICE_SUMMARY_PATH = Path("LGEA/data/runs/service_surface_latest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a FastAPI live run against /api/v1/chat/ for every question in "
            "LGEA/configs/baseline_questions.json."
        )
    )
    parser.add_argument("--questions-path", default=str(DEFAULT_QUESTIONS_PATH))
    parser.add_argument("--results-output", default=str(DEFAULT_RESULTS_PATH))
    parser.add_argument("--summary-output", default=str(DEFAULT_SUMMARY_PATH))
    parser.add_argument(
        "--service-results-output", default=str(DEFAULT_SERVICE_RESULTS_PATH)
    )
    parser.add_argument(
        "--service-summary-output", default=str(DEFAULT_SERVICE_SUMMARY_PATH)
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--session-id", default="")
    parser.add_argument("--user-id", default="lgea-fastapi-runner")
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument(
        "--skip-service-surface-checks",
        action="store_true",
        help="Skip internal service-surface checks after the FastAPI live run.",
    )
    return parser.parse_args()


def _read_questions(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("questions", [])


def main() -> None:
    args = parse_args()
    questions_path = Path(args.questions_path)
    results_output = Path(args.results_output)
    summary_output = Path(args.summary_output)
    service_results_output = Path(args.service_results_output)
    service_summary_output = Path(args.service_summary_output)
    questions = _read_questions(questions_path)

    session_id = args.session_id or datetime.now().strftime("fastapi-%Y%m%d-%H%M%S")
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
        notes="FastAPI live run initialized.",
    )

    processed_runs = 0
    with httpx.Client(base_url=args.base_url, timeout=args.timeout_seconds) as client:
        for item in questions:
            run_id = f"fastapi-live__{item['persona_id']}__{item['question_id']}"
            write_result_record(
                results_output,
                run_id=run_id,
                model_id="lumi-fastapi",
                persona_id=item["persona_id"],
                question_id=item["question_id"],
                evaluation_surface=item["evaluation_surface"],
                attack_type=item["attack_type"],
                status="queued",
                prompt_text=item["prompt"],
                system_prompt="fastapi-live:/api/v1/chat/",
                mode="live",
                notes="FastAPI live run queued.",
            )

            try:
                response = client.post(
                    "/api/v1/chat/",
                    json={
                        "message": item["prompt"],
                        "session_id": session_id,
                        "user_id": args.user_id,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                status = "completed"
                answer_text = payload.get("message", "")
                notes = json.dumps(
                    {
                        "tool_used": payload.get("tool_used"),
                        "cached": payload.get("cached"),
                    },
                    ensure_ascii=False,
                )
            except Exception as exc:
                status = "failed_http_request"
                answer_text = ""
                notes = f"{type(exc).__name__}: {exc}"

            write_result_record(
                results_output,
                run_id=run_id,
                model_id="lumi-fastapi",
                persona_id=item["persona_id"],
                question_id=item["question_id"],
                evaluation_surface=item["evaluation_surface"],
                attack_type=item["attack_type"],
                status=status,
                prompt_text=item["prompt"],
                system_prompt="fastapi-live:/api/v1/chat/",
                response_text=answer_text,
                used_model_name="lumi-fastapi",
                mode="live",
                notes=notes,
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
        notes="FastAPI live run completed.",
    )

    if not args.skip_service_surface_checks:
        surface_questions = {
            "router",
            "response-layer",
            "rag",
            "tool",
        }
        asyncio.run(
            run_service_surface_checks(
                questions_path=questions_path,
                results_output=service_results_output,
                summary_output=service_summary_output,
                only_surfaces=surface_questions,
                session_prefix="surface",
                manifest_note=(
                    "Local service-surface runner initialized from FastAPI live run."
                ),
                completion_note=(
                    "Local service-surface runner completed from FastAPI live run."
                ),
            )
        )
    print(results_output)
    print(summary_output)


if __name__ == "__main__":
    main()
