from __future__ import annotations

import json
import os
from pathlib import Path

REPORTS_ROOT = Path("LGEA/reports")
BATCHES_ROOT = REPORTS_ROOT / "batches"
ENV_BATCH_DIR = "LGEA_REPORT_BATCH_DIR"
ENV_BATCH_LABEL = "LGEA_REPORT_BATCH_LABEL"


def get_active_batch_dir() -> Path | None:
    raw_value = os.getenv(ENV_BATCH_DIR, "").strip()
    if not raw_value:
        return None
    return Path(raw_value)


def resolve_report_output(filename: str, *, fallback_root: Path | None = None) -> Path:
    batch_dir = get_active_batch_dir()
    if batch_dir is not None:
        batch_dir.mkdir(parents=True, exist_ok=True)
        return batch_dir / filename
    root = fallback_root or REPORTS_ROOT
    root.mkdir(parents=True, exist_ok=True)
    return root / filename


def next_batch_dir() -> Path:
    BATCHES_ROOT.mkdir(parents=True, exist_ok=True)
    existing_numbers: list[int] = []
    for child in BATCHES_ROOT.iterdir():
        if not child.is_dir():
            continue
        prefix = child.name.split("_", 1)[0]
        try:
            existing_numbers.append(int(prefix))
        except ValueError:
            continue
    next_number = max(existing_numbers, default=0) + 1
    return BATCHES_ROOT / f"{next_number:03d}_test"


def write_batch_manifest(
    batch_dir: Path,
    *,
    batch_label: str,
    session_id: str,
    questions_path: Path,
    base_url: str,
) -> Path:
    batch_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "batch_label": batch_label,
        "session_id": session_id,
        "questions_path": str(questions_path),
        "base_url": base_url,
        "status": "running",
        "stages": {},
    }
    output_path = batch_dir / "batch_manifest.json"
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def update_batch_manifest(
    manifest_path: Path,
    *,
    status: str | None = None,
    stage_name: str | None = None,
    stage_status: str | None = None,
    stage_notes: str | None = None,
) -> Path:
    payload: dict = {}
    if manifest_path.exists():
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    if status is not None:
        payload["status"] = status

    if stage_name:
        stages = payload.setdefault("stages", {})
        stage_payload = stages.setdefault(stage_name, {})
        if stage_status is not None:
            stage_payload["status"] = stage_status
        if stage_notes is not None:
            stage_payload["notes"] = stage_notes

    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest_path
