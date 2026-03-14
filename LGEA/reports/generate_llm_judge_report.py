from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

INPUT_PATH = Path("LGEA/data/judge/llm_scored_results.jsonl")
MANIFEST_FILENAME = "batch_manifest.json"


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _load_active_batch_context() -> tuple[str, set[str]]:
    batch_dir_raw = os.getenv("LGEA_REPORT_BATCH_DIR", "").strip()
    if not batch_dir_raw:
        return "", set()
    manifest_path = Path(batch_dir_raw) / MANIFEST_FILENAME
    if not manifest_path.exists():
        return "", set()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    questions_path = Path(manifest.get("questions_path", ""))
    question_ids: set[str] = set()
    if questions_path.exists():
        payload = json.loads(questions_path.read_text(encoding="utf-8"))
        question_ids = {item["question_id"] for item in payload.get("questions", [])}
    return manifest.get("session_id", ""), question_ids


def main() -> None:
    from LGEA.reports.batching import resolve_report_output

    rows = _read_jsonl(INPUT_PATH)
    session_id, question_ids = _load_active_batch_context()
    if session_id:
        rows = [row for row in rows if row.get("session_id") == session_id]
    elif question_ids:
        rows = [row for row in rows if row.get("question_id") in question_ids]
    scored_rows = [row for row in rows if row.get("judge_status") == "scored"]
    skipped_rows = [row for row in rows if row.get("judge_status") != "scored"]
    lines = [
        "# LGEA LLM Judge 보고서",
        "",
        "- judge 모델: `solar-pro2`",
        f"- 전체 레코드 수: {len(rows)}",
        f"- 채점 완료 수: {len(scored_rows)}",
        f"- 미채점 수: {len(skipped_rows)}",
        "",
    ]

    for row in scored_rows:
        lines.extend(
            [
                f"## {row['run_id']}",
                "",
                f"- 질문 ID: `{row['question_id']}`",
                f"- 평가 표면: `{row['evaluation_surface']}`",
                f"- 위험 라벨: `{row.get('risk_label') or '(없음)'}`",
                f"- LLM 점수: `{row.get('judge_score')}`",
                f"- LLM 판정: `{row.get('judge_rating')}`",
                f"- 거부 감지: `{row.get('refusal_detected')}`",
                f"- 유해 지원 감지: `{row.get('unsafe_assistance_detected')}`",
                f"- 신뢰도: `{row.get('confidence')}`",
                f"- 근거: {row.get('judge_reason') or '(없음)'}",
                f"- 정책 정렬: {row.get('policy_alignment') or '(없음)'}",
                "",
            ]
        )

    if skipped_rows:
        lines.extend(
            [
                "## 미채점 항목",
                "",
            ]
        )
        for row in skipped_rows:
            lines.extend(
                [
                    f"- `{row.get('run_id', '(없음)')}`: {row.get('judge_reason', '(없음)')}",
                ]
            )
        lines.append("")

    output_path = resolve_report_output("llm_judge_report_ko.md")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
