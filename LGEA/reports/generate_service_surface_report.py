from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

INPUT_PATH = Path("LGEA/data/runs/service_surface_results.jsonl")
QUESTIONS_PATH = Path("LGEA/configs/baseline_questions.json")


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _resolve_output_path(path: Path) -> Path:
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    counter = 1
    while True:
        candidate = path.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _load_question_index(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        item["question_id"]: item
        for item in payload.get("questions", [])
        if item.get("question_id")
    }


def _count_by_surface(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        surface = row.get("evaluation_surface", "unknown")
        counts[surface] = counts.get(surface, 0) + 1
    return counts


def _field(row: dict, question_meta: dict, key: str, fallback: str = "(없음)") -> str:
    value = row.get(key)
    if value is None:
        value = question_meta.get(key)
    if value in (None, ""):
        return fallback
    return str(value)


def _add_question_block(
    lines: list[str], row: dict, question_index: dict[str, dict]
) -> None:
    question_meta = question_index.get(row.get("question_id", ""), {})
    lines.extend(
        [
            f"## {row['run_id']}",
            "",
            "### 실행 메타데이터",
            "",
            f"- 상태: `{row['status']}`",
            f"- 생성 시각: `{row.get('created_at', '(없음)')}`",
            f"- 평가 표면: `{_field(row, question_meta, 'evaluation_surface')}`",
            f"- 카테고리: `{_field(row, question_meta, 'category')}`",
            f"- 페르소나 라벨: `{row.get('persona_id', '(없음)')}`",
            f"- 질문 ID: `{row.get('question_id', '(없음)')}`",
            f"- 공격 유형: `{_field(row, question_meta, 'attack_type')}`",
            f"- 위험 라벨: `{_field(row, question_meta, 'risk_label')}`",
            f"- 프롬프트 전략: `{_field(row, question_meta, 'prompt_strategy')}`",
            f"- 평가 목적: {_field(row, question_meta, 'evaluation_goal')}",
            f"- 기대 안전행동: {_field(row, question_meta, 'expected_safe_behavior')}",
            f"- 질문 출처: `{_field(row, question_meta, 'source_type')}`",
            f"- 시스템 프롬프트/경로: {row.get('system_prompt') or '(없음)'}",
            f"- 메모: {row.get('notes') or '(없음)'}",
            "",
            "### 질문",
            "",
            row.get("prompt_text") or "(질문 기록 없음)",
            "",
            "### 응답",
            "",
            row.get("response_text") or "(응답 기록 없음)",
            "",
        ]
    )


def main() -> None:
    from LGEA.reports.batching import resolve_report_output

    rows = _read_jsonl(INPUT_PATH)
    question_index = _load_question_index(QUESTIONS_PATH)
    latest_rows: dict[str, dict] = {}
    for row in rows:
        latest_rows[row["run_id"]] = row

    final_rows = list(latest_rows.values())
    final_rows.sort(key=lambda item: item["run_id"])
    completed_count = sum(1 for row in final_rows if row["status"] == "completed")
    surface_counts = _count_by_surface(final_rows)

    lines = [
        "# LGEA 서비스 Surface Live Run 보고서",
        "",
        "현재 브랜치의 실제 서비스 내부 경로 `router`, `response-layer`, `rag`, `tool` 점검 결과를",
        "질문 메타데이터와 함께 정리한 보고서다.",
        "",
        "## 실행 요약",
        "",
        f"- 총 실행 항목 수: {len(final_rows)}",
        f"- 완료 항목 수: {completed_count}",
        f"- 실패 항목 수: {len(final_rows) - completed_count}",
        "",
        "## 표면별 건수",
        "",
        "| 평가 표면 | 건수 |",
        "| --- | --- |",
    ]

    for surface, count in sorted(surface_counts.items()):
        lines.append(f"| {surface} | {count} |")

    lines.append("")
    for row in final_rows:
        _add_question_block(lines, row, question_index)

    output_path = _resolve_output_path(
        resolve_report_output("service_surface_live_report_ko.md")
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
