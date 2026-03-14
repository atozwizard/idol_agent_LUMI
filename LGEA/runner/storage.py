from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class RunManifest:
    session_id: str
    created_at: str
    completed_at: str | None
    status: str
    mode: str
    execute_live: bool
    plan_path: str
    matrix_path: str
    results_path: str
    matrix_size: int
    processed_runs: int
    notes: str | None = None


@dataclass(frozen=True)
class ResultRecord:
    run_id: str
    model_id: str
    persona_id: str
    question_id: str
    evaluation_surface: str
    attack_type: str
    status: str
    created_at: str
    session_id: str | None = None
    category: str | None = None
    risk_label: str | None = None
    prompt_strategy: str | None = None
    evaluation_goal: str | None = None
    expected_safe_behavior: str | None = None
    source_type: str | None = None
    prompt_text: str | None = None
    system_prompt: str | None = None
    response_text: str | None = None
    score: float | None = None
    used_model_name: str | None = None
    mode: str | None = None
    notes: str | None = None


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def write_run_manifest(
    path: Path,
    *,
    session_id: str,
    status: str,
    mode: str,
    execute_live: bool,
    plan_path: Path,
    matrix_path: Path,
    results_path: Path,
    matrix_size: int,
    processed_runs: int,
    created_at: str,
    completed_at: str | None = None,
    notes: str | None = None,
) -> RunManifest:
    manifest = RunManifest(
        session_id=session_id,
        created_at=created_at,
        completed_at=completed_at,
        status=status,
        mode=mode,
        execute_live=execute_live,
        plan_path=str(plan_path),
        matrix_path=str(matrix_path),
        results_path=str(results_path),
        matrix_size=matrix_size,
        processed_runs=processed_runs,
        notes=notes,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(manifest), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def write_result_record(
    path: Path,
    *,
    run_id: str,
    model_id: str,
    persona_id: str,
    question_id: str,
    evaluation_surface: str,
    attack_type: str,
    status: str = "planned",
    session_id: str | None = None,
    category: str | None = None,
    risk_label: str | None = None,
    prompt_strategy: str | None = None,
    evaluation_goal: str | None = None,
    expected_safe_behavior: str | None = None,
    source_type: str | None = None,
    prompt_text: str | None = None,
    system_prompt: str | None = None,
    response_text: str | None = None,
    score: float | None = None,
    used_model_name: str | None = None,
    mode: str | None = None,
    notes: str | None = None,
) -> ResultRecord:
    record = ResultRecord(
        run_id=run_id,
        model_id=model_id,
        persona_id=persona_id,
        question_id=question_id,
        session_id=session_id,
        evaluation_surface=evaluation_surface,
        attack_type=attack_type,
        status=status,
        created_at=datetime.now().isoformat(timespec="seconds"),
        category=category,
        risk_label=risk_label,
        prompt_strategy=prompt_strategy,
        evaluation_goal=evaluation_goal,
        expected_safe_behavior=expected_safe_behavior,
        source_type=source_type,
        prompt_text=prompt_text,
        system_prompt=system_prompt,
        response_text=response_text,
        score=score,
        used_model_name=used_model_name,
        mode=mode,
        notes=notes,
    )
    append_jsonl(path, asdict(record))
    return record
