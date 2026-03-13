from __future__ import annotations

import json
from pathlib import Path

INPUT_PATH = Path("LGEA/data/runs/fastapi_live_results.jsonl")
OUTPUT_PATH = Path("LGEA/reports/fastapi_live_run_report_ko.md")


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    rows = _read_jsonl(INPUT_PATH)
    final_rows: dict[str, dict] = {}
    for row in rows:
        final_rows[row["run_id"]] = row

    completed = list(final_rows.values())
    completed.sort(key=lambda item: item["run_id"])

    lines = [
        "# LGEA FastAPI Live Run 보고서",
        "",
        "실제 FastAPI `/api/v1/chat/` 엔드포인트를 대상으로 수행한 1차 live run 결과입니다.",
        "",
        f"- 총 실행 수: {len(completed)}",
        f"- 완료 수: {sum(1 for row in completed if row['status'] == 'completed')}",
        "",
    ]

    for row in completed:
        lines.extend(
            [
                f"## {row['run_id']}",
                "",
                f"- 상태: `{row['status']}`",
                f"- 카테고리: `{row['persona_id']}`",
                f"- 질문 ID: `{row['question_id']}`",
                f"- 평가 대상: `{row['evaluation_surface']}`",
                f"- 메모: {row.get('notes') or '(없음)'}",
                "",
                "질문:",
                "",
                row.get("prompt_text") or "(질문 기록 없음)",
                "",
                "응답:",
                "",
                row.get("response_text") or "(응답 기록 없음)",
                "",
            ]
        )

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
