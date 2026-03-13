from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_SCORES_INPUT = Path("LGEA/data/judge/scored_results.jsonl")
DEFAULT_SUMMARY_OUTPUT = Path("LGEA/data/analysis/summary.json")
DEFAULT_MODEL_OUTPUT = Path("LGEA/data/analysis/model_summary.json")
DEFAULT_PERSONA_OUTPUT = Path("LGEA/data/analysis/persona_summary.json")
DEFAULT_REPORT_OUTPUT = Path("LGEA/reports/analysis_summary.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate LGEA scored results.")
    parser.add_argument(
        "--scores-input",
        default=str(DEFAULT_SCORES_INPUT),
        help="Path to scored results JSONL.",
    )
    parser.add_argument(
        "--summary-output",
        default=str(DEFAULT_SUMMARY_OUTPUT),
        help="Path to overall summary JSON.",
    )
    parser.add_argument(
        "--model-output",
        default=str(DEFAULT_MODEL_OUTPUT),
        help="Path to model-level summary JSON.",
    )
    parser.add_argument(
        "--persona-output",
        default=str(DEFAULT_PERSONA_OUTPUT),
        help="Path to persona-level summary JSON.",
    )
    parser.add_argument(
        "--report-output",
        default=str(DEFAULT_REPORT_OUTPUT),
        help="Path to report-ready Markdown summary.",
    )
    return parser.parse_args()


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def _build_group_rows(grouped: dict[str, list[dict]], group_key: str) -> list[dict]:
    from LGEA.analysis.statistics import build_metrics

    rows: list[dict] = []
    for group_value, items in sorted(grouped.items()):
        metrics = build_metrics(items)
        rows.append(
            {
                group_key: group_value,
                **asdict(metrics),
            }
        )
    return rows


def _write_markdown_report(
    path: Path,
    *,
    overall: dict,
    model_rows: list[dict],
    persona_rows: list[dict],
) -> Path:
    from LGEA.analysis.visualize import render_markdown_table

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# LGEA Analysis Summary",
        "",
        "## Overall",
        "",
        f"- total_runs: {overall['total_runs']}",
        f"- scored_runs: {overall['scored_runs']}",
        f"- refusal_rate: {overall['refusal_rate']}",
        f"- attack_success_rate: {overall['attack_success_rate']}",
        "",
        "## Model Summary",
        "",
        render_markdown_table(
            model_rows,
            [
                "model_id",
                "total_runs",
                "scored_runs",
                "refused_runs",
                "unsafe_runs",
                "refusal_rate",
                "attack_success_rate",
            ],
        ),
        "",
        "## Persona Summary",
        "",
        render_markdown_table(
            persona_rows,
            [
                "persona_id",
                "total_runs",
                "scored_runs",
                "refused_runs",
                "unsafe_runs",
                "refusal_rate",
                "attack_success_rate",
            ],
        ),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    from LGEA.analysis.statistics import build_metrics, group_by

    args = parse_args()
    scores_input = Path(args.scores_input)
    summary_output = Path(args.summary_output)
    model_output = Path(args.model_output)
    persona_output = Path(args.persona_output)
    report_output = Path(args.report_output)

    records = _read_jsonl(scores_input)
    overall = asdict(build_metrics(records))
    model_rows = _build_group_rows(group_by(records, "model_id"), "model_id")
    persona_rows = _build_group_rows(group_by(records, "persona_id"), "persona_id")

    _write_json(summary_output, overall)
    _write_json(model_output, model_rows)
    _write_json(persona_output, persona_rows)
    _write_markdown_report(
        report_output,
        overall=overall,
        model_rows=model_rows,
        persona_rows=persona_rows,
    )

    print(summary_output)
    print(model_output)
    print(persona_output)
    print(report_output)


if __name__ == "__main__":
    main()
