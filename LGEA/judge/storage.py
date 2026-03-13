from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class FinalRunRecord:
    run_id: str
    model_id: str
    persona_id: str
    question_id: str
    attack_type: str
    status: str
    created_at: str
    prompt_text: str | None
    system_prompt: str | None
    response_text: str | None
    score: float | None
    used_model_name: str | None
    mode: str | None
    notes: str | None


@dataclass(frozen=True)
class ScoredResultRecord:
    run_id: str
    model_id: str
    persona_id: str
    question_id: str
    attack_type: str
    status: str
    mode: str | None
    used_model_name: str | None
    prompt_text: str | None
    system_prompt: str | None
    response_text: str | None
    judge_status: str
    judge_score: int | None
    judge_rating: str
    judge_reason: str
    rubric_version: int
    notes: str | None


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def load_final_run_records(path: Path) -> list[FinalRunRecord]:
    final_by_run: dict[str, dict] = {}
    for row in _read_jsonl(path):
        final_by_run[row["run_id"]] = row
    return [
        FinalRunRecord(
            run_id=row["run_id"],
            model_id=row["model_id"],
            persona_id=row["persona_id"],
            question_id=row["question_id"],
            attack_type=row["attack_type"],
            status=row["status"],
            created_at=row["created_at"],
            prompt_text=row.get("prompt_text"),
            system_prompt=row.get("system_prompt"),
            response_text=row.get("response_text"),
            score=row.get("score"),
            used_model_name=row.get("used_model_name"),
            mode=row.get("mode"),
            notes=row.get("notes"),
        )
        for row in final_by_run.values()
    ]


def write_scored_results(path: Path, records: list[ScoredResultRecord]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    return path
