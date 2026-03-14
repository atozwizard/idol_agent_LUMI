from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_QUESTIONS_PATH = Path("LGEA/configs/baseline_questions.json")
DEFAULT_RESULTS_PATH = Path("LGEA/data/runs/fastapi_live_results.jsonl")
DEFAULT_SUMMARY_PATH = Path("LGEA/data/runs/fastapi_live_latest.json")
DEFAULT_SERVICE_RESULTS_PATH = Path("LGEA/data/runs/service_surface_results.jsonl")
DEFAULT_SERVICE_SUMMARY_PATH = Path("LGEA/data/runs/service_surface_latest.json")
DEFAULT_LLM_JUDGE_OUTPUT = Path("LGEA/data/judge/llm_scored_results.jsonl")
DEFAULT_EXPANDED_QUESTIONS_OUTPUT = Path(
    "LGEA/data/questions/stress_expanded_questions.json"
)


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
    parser.add_argument(
        "--skip-llm-judge",
        action="store_true",
        help="Skip solar-pro2 LLM judge after the FastAPI live run.",
    )
    parser.add_argument(
        "--skip-question-expander",
        action="store_true",
        help="Skip solar-pro2 stress question expansion after the FastAPI live run.",
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip cross-surface, comparative, and thesis-ready analysis after the run.",
    )
    parser.add_argument(
        "--llm-judge-output",
        default=str(DEFAULT_LLM_JUDGE_OUTPUT),
    )
    parser.add_argument(
        "--expanded-questions-output",
        default=str(DEFAULT_EXPANDED_QUESTIONS_OUTPUT),
    )
    return parser.parse_args()


def _read_questions(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("questions", [])


def _load_storage_writers():
    from LGEA.runner.storage import write_result_record, write_run_manifest

    return write_result_record, write_run_manifest


def _load_report_generators():
    from LGEA.reports.generate_fastapi_live_report import (
        main as generate_fastapi_report,
    )
    from LGEA.reports.generate_presentation_outline import (
        main as generate_presentation_outline,
    )
    from LGEA.reports.generate_service_surface_report import (
        main as generate_service_surface_report,
    )
    from LGEA.reports.generate_thesis_ready_report import (
        main as generate_thesis_ready_report,
    )

    return (
        generate_fastapi_report,
        generate_service_surface_report,
        generate_presentation_outline,
        generate_thesis_ready_report,
    )


def _resolve_project_python() -> str:
    venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _run_service_surface_runner(
    *,
    questions_path: Path,
    results_output: Path,
    summary_output: Path,
    session_id: str,
) -> None:
    command = [
        _resolve_project_python(),
        "LGEA/runner/service_surface_runner.py",
        "--questions-path",
        str(questions_path),
        "--results-output",
        str(results_output),
        "--summary-output",
        str(summary_output),
        "--session-id",
        session_id,
        "--only-surfaces",
        "router,response-layer,rag,tool",
    ]
    subprocess.run(command, check=True, cwd=PROJECT_ROOT)


def _run_subprocess_stage(command: list[str], *, stage_name: str) -> bool:
    try:
        completed = subprocess.run(
            command,
            check=True,
            cwd=PROJECT_ROOT,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        details = stderr or stdout or str(exc)
        print(f"[LGEA] stage failed: {stage_name}: {details}")
        return False
    if completed.stdout:
        print(completed.stdout.strip())
    return True


def _run_llm_judge(
    *,
    results_input: Path,
    scores_output: Path,
    questions_path: Path,
    session_id: str,
) -> bool:
    command = [
        _resolve_project_python(),
        "LGEA/judge/llm_judge.py",
        "--results-input",
        str(results_input),
        "--scores-output",
        str(scores_output),
        "--questions-path",
        str(questions_path),
        "--session-id",
        session_id,
    ]
    return _run_subprocess_stage(command, stage_name="llm_judge")


def _run_question_expander(
    *,
    questions_path: Path,
    output_path: Path,
) -> bool:
    command = [
        _resolve_project_python(),
        "LGEA/prompts/question_expander.py",
        "--questions-input",
        str(questions_path),
        "--output-path",
        str(output_path),
        "--expansion-mode",
        "stress",
    ]
    return _run_subprocess_stage(command, stage_name="question_expander")


def _run_analysis_pipeline(*, fastapi_input: Path, service_input: Path) -> None:
    stage_commands = [
        (
            "cross_surface_analysis",
            [
                _resolve_project_python(),
                "LGEA/analysis/cross_surface_analysis.py",
                "--fastapi-input",
                str(fastapi_input),
                "--service-input",
                str(service_input),
            ],
        ),
        (
            "comparative_analysis",
            [
                _resolve_project_python(),
                "LGEA/analysis/comparative_analysis.py",
                "--fastapi-input",
                str(fastapi_input),
                "--service-input",
                str(service_input),
            ],
        ),
        (
            "repetition_plan",
            [
                _resolve_project_python(),
                "LGEA/runner/repetition_plan.py",
            ],
        ),
        (
            "thesis_ready_report",
            [
                _resolve_project_python(),
                "LGEA/reports/generate_thesis_ready_report.py",
            ],
        ),
    ]
    for stage_name, command in stage_commands:
        _run_subprocess_stage(command, stage_name=stage_name)


def main() -> None:
    args = parse_args()
    write_result_record, write_run_manifest = _load_storage_writers()
    (
        generate_fastapi_report,
        generate_service_surface_report,
        generate_presentation_outline,
        generate_thesis_ready_report,
    ) = _load_report_generators()
    from LGEA.reports.batching import (
        next_batch_dir,
        update_batch_manifest,
        write_batch_manifest,
    )

    questions_path = Path(args.questions_path)
    results_output = Path(args.results_output)
    summary_output = Path(args.summary_output)
    service_results_output = Path(args.service_results_output)
    service_summary_output = Path(args.service_summary_output)
    llm_judge_output = Path(args.llm_judge_output)
    expanded_questions_output = Path(args.expanded_questions_output)
    questions = _read_questions(questions_path)

    session_id = args.session_id or datetime.now().strftime("fastapi-%Y%m%d-%H%M%S")
    created_at = datetime.now().isoformat(timespec="seconds")
    batch_dir = next_batch_dir()
    batch_label = batch_dir.name
    os.environ["LGEA_REPORT_BATCH_DIR"] = str(batch_dir)
    os.environ["LGEA_REPORT_BATCH_LABEL"] = batch_label
    manifest_path = write_batch_manifest(
        batch_dir,
        batch_label=batch_label,
        session_id=session_id,
        questions_path=questions_path,
        base_url=args.base_url,
    )
    stage_failures: list[str] = []

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
                session_id=session_id,
                evaluation_surface=item["evaluation_surface"],
                attack_type=item["attack_type"],
                status="queued",
                category=item.get("category"),
                risk_label=item.get("risk_label"),
                prompt_strategy=item.get("prompt_strategy"),
                evaluation_goal=item.get("evaluation_goal"),
                expected_safe_behavior=item.get("expected_safe_behavior"),
                source_type=item.get("source_type"),
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
                session_id=session_id,
                evaluation_surface=item["evaluation_surface"],
                attack_type=item["attack_type"],
                status=status,
                category=item.get("category"),
                risk_label=item.get("risk_label"),
                prompt_strategy=item.get("prompt_strategy"),
                evaluation_goal=item.get("evaluation_goal"),
                expected_safe_behavior=item.get("expected_safe_behavior"),
                source_type=item.get("source_type"),
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
    result_rows = [
        json.loads(line)
        for line in results_output.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    current_rows = [row for row in result_rows if row.get("session_id") == session_id]
    completed_count = sum(1 for row in current_rows if row.get("status") == "completed")
    failed_count = sum(
        1 for row in current_rows if row.get("status") == "failed_http_request"
    )
    fastapi_stage_status = "completed" if failed_count == 0 else "partial_failed"
    if failed_count:
        stage_failures.append("fastapi_live_run")
    update_batch_manifest(
        manifest_path,
        stage_name="fastapi_live_run",
        stage_status=fastapi_stage_status,
        stage_notes=(
            f"completed={completed_count}, failed_http_request={failed_count}, "
            f"total={len(current_rows)}"
        ),
    )

    if not args.skip_service_surface_checks:
        try:
            _run_service_surface_runner(
                questions_path=questions_path,
                results_output=service_results_output,
                summary_output=service_summary_output,
                session_id=session_id,
            )
            update_batch_manifest(
                manifest_path,
                stage_name="service_surface_runner",
                stage_status="completed",
                stage_notes="service surface checks completed.",
            )
        except subprocess.CalledProcessError as exc:
            stage_failures.append("service_surface_runner")
            update_batch_manifest(
                manifest_path,
                stage_name="service_surface_runner",
                stage_status="failed",
                stage_notes=str(exc),
            )
    else:
        update_batch_manifest(
            manifest_path,
            stage_name="service_surface_runner",
            stage_status="skipped",
            stage_notes="Skipped by CLI flag.",
        )

    generate_fastapi_report()
    update_batch_manifest(
        manifest_path,
        stage_name="generate_fastapi_report",
        stage_status="completed",
        stage_notes="FastAPI report generated.",
    )
    if not args.skip_service_surface_checks:
        generate_service_surface_report()
        update_batch_manifest(
            manifest_path,
            stage_name="generate_service_surface_report",
            stage_status="completed",
            stage_notes="Service-surface report generated.",
        )
    if not args.skip_llm_judge:
        llm_judge_success = _run_llm_judge(
            results_input=results_output,
            scores_output=llm_judge_output,
            questions_path=questions_path,
            session_id=session_id,
        )
        update_batch_manifest(
            manifest_path,
            stage_name="llm_judge",
            stage_status="completed" if llm_judge_success else "failed",
            stage_notes=(
                "LLM judge completed."
                if llm_judge_success
                else "LLM judge stage failed. See console logs."
            ),
        )
        if not llm_judge_success:
            stage_failures.append("llm_judge")
        if llm_judge_success:
            llm_report_success = _run_subprocess_stage(
                [
                    _resolve_project_python(),
                    "LGEA/reports/generate_llm_judge_report.py",
                ],
                stage_name="generate_llm_judge_report",
            )
            update_batch_manifest(
                manifest_path,
                stage_name="generate_llm_judge_report",
                stage_status="completed" if llm_report_success else "failed",
                stage_notes=(
                    "LLM judge report generated."
                    if llm_report_success
                    else "Failed to generate LLM judge report."
                ),
            )
            if not llm_report_success:
                stage_failures.append("generate_llm_judge_report")
    else:
        update_batch_manifest(
            manifest_path,
            stage_name="llm_judge",
            stage_status="skipped",
            stage_notes="Skipped by CLI flag.",
        )
    if not args.skip_question_expander:
        expander_success = _run_question_expander(
            questions_path=questions_path,
            output_path=expanded_questions_output,
        )
        update_batch_manifest(
            manifest_path,
            stage_name="question_expander",
            stage_status="completed" if expander_success else "failed",
            stage_notes=(
                "Question expander completed."
                if expander_success
                else "Question expander stage failed. See console logs."
            ),
        )
        if not expander_success:
            stage_failures.append("question_expander")
        if expander_success:
            expansion_report_success = _run_subprocess_stage(
                [
                    _resolve_project_python(),
                    "LGEA/reports/generate_question_expansion_report.py",
                ],
                stage_name="generate_question_expansion_report",
            )
            update_batch_manifest(
                manifest_path,
                stage_name="generate_question_expansion_report",
                stage_status="completed" if expansion_report_success else "failed",
                stage_notes=(
                    "Question expansion report generated."
                    if expansion_report_success
                    else "Failed to generate question expansion report."
                ),
            )
            if not expansion_report_success:
                stage_failures.append("generate_question_expansion_report")
    else:
        update_batch_manifest(
            manifest_path,
            stage_name="question_expander",
            stage_status="skipped",
            stage_notes="Skipped by CLI flag.",
        )
    if not args.skip_analysis:
        _run_analysis_pipeline(
            fastapi_input=results_output,
            service_input=service_results_output,
        )
        update_batch_manifest(
            manifest_path,
            stage_name="analysis_pipeline",
            stage_status="completed",
            stage_notes="Cross-surface, comparative, repetition, thesis pipeline ran.",
        )
        generate_thesis_ready_report()
        update_batch_manifest(
            manifest_path,
            stage_name="generate_thesis_ready_report",
            stage_status="completed",
            stage_notes="Thesis-ready report generated.",
        )
        generate_presentation_outline()
        update_batch_manifest(
            manifest_path,
            stage_name="generate_presentation_outline",
            stage_status="completed",
            stage_notes="Presentation outline generated.",
        )
    else:
        generate_presentation_outline()
        update_batch_manifest(
            manifest_path,
            stage_name="analysis_pipeline",
            stage_status="skipped",
            stage_notes="Skipped by CLI flag.",
        )
        update_batch_manifest(
            manifest_path,
            stage_name="generate_presentation_outline",
            stage_status="completed",
            stage_notes="Presentation outline generated.",
        )
    final_batch_status = "completed" if not stage_failures else "partial_failed"
    update_batch_manifest(
        manifest_path,
        status=final_batch_status,
        stage_name="batch",
        stage_status=final_batch_status,
        stage_notes=(
            "All stages completed cleanly."
            if not stage_failures
            else "Failed or partial stages: " + ", ".join(stage_failures)
        ),
    )
    print(results_output)
    print(summary_output)


if __name__ == "__main__":
    main()
