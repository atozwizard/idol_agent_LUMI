from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ResultRecord:
    run_id: str
    model_id: str
    persona_id: str
    question_id: str
    attack_type: str
    status: str
    created_at: str
    response_text: str | None = None
    score: float | None = None
    notes: str | None = None


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def write_result_record(
    path: Path,
    *,
    run_id: str,
    model_id: str,
    persona_id: str,
    question_id: str,
    attack_type: str,
    status: str = "planned",
    response_text: str | None = None,
    score: float | None = None,
    notes: str | None = None,
) -> ResultRecord:
    record = ResultRecord(
        run_id=run_id,
        model_id=model_id,
        persona_id=persona_id,
        question_id=question_id,
        attack_type=attack_type,
        status=status,
        created_at=datetime.now().isoformat(timespec="seconds"),
        response_text=response_text,
        score=score,
        notes=notes,
    )
    append_jsonl(path, asdict(record))
    return record
