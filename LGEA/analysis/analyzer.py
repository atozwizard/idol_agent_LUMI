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
DEFAULT_SURFACE_OUTPUT = Path("LGEA/data/analysis/surface_summary.json")
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
        "--surface-output",
        default=str(DEFAULT_SURFACE_OUTPUT),
        help="Path to evaluation-surface-level summary JSON.",
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
    surface_rows: list[dict],
) -> Path:
    from LGEA.analysis.visualize import render_markdown_table

    path.parent.mkdir(parents=True, exist_ok=True)
    model_table_rows = [
        {
            "모델": row["model_id"],
            "전체 실행수": row["total_runs"],
            "채점 수": row["scored_runs"],
            "거부 수": row["refused_runs"],
            "위험 응답 수": row["unsafe_runs"],
            "거부율": row["refusal_rate"],
            "공격 성공률": row["attack_success_rate"],
        }
        for row in model_rows
    ]
    persona_table_rows = [
        {
            "카테고리": row["persona_id"],
            "전체 실행수": row["total_runs"],
            "채점 수": row["scored_runs"],
            "거부 수": row["refused_runs"],
            "위험 응답 수": row["unsafe_runs"],
            "거부율": row["refusal_rate"],
            "공격 성공률": row["attack_success_rate"],
        }
        for row in persona_rows
    ]
    surface_table_rows = [
        {
            "평가 대상": row["evaluation_surface"],
            "전체 실행수": row["total_runs"],
            "채점 수": row["scored_runs"],
            "거부 수": row["refused_runs"],
            "위험 응답 수": row["unsafe_runs"],
            "거부율": row["refusal_rate"],
            "공격 성공률": row["attack_success_rate"],
        }
        for row in surface_rows
    ]
    lines = [
        "# LGEA 분석 요약",
        "",
        "## 전체 요약",
        "",
        f"- 전체 실행 수: {overall['total_runs']}",
        f"- 채점 완료 수: {overall['scored_runs']}",
        f"- 미채점 수: {overall['not_scored_runs']}",
        f"- 거부율: {overall['refusal_rate']}",
        f"- 공격 성공률: {overall['attack_success_rate']}",
        "",
        "## 모델별 요약",
        "",
        render_markdown_table(
            model_table_rows,
            [
                "모델",
                "전체 실행수",
                "채점 수",
                "거부 수",
                "위험 응답 수",
                "거부율",
                "공격 성공률",
            ],
        ),
        "",
        "## 카테고리별 요약",
        "",
        render_markdown_table(
            persona_table_rows,
            [
                "카테고리",
                "전체 실행수",
                "채점 수",
                "거부 수",
                "위험 응답 수",
                "거부율",
                "공격 성공률",
            ],
        ),
        "",
        "## 평가 대상별 요약",
        "",
        render_markdown_table(
            surface_table_rows,
            [
                "평가 대상",
                "전체 실행수",
                "채점 수",
                "거부 수",
                "위험 응답 수",
                "거부율",
                "공격 성공률",
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
    surface_output = Path(args.surface_output)
    report_output = Path(args.report_output)

    records = _read_jsonl(scores_input)
    overall = asdict(build_metrics(records))
    model_rows = _build_group_rows(group_by(records, "model_id"), "model_id")
    persona_rows = _build_group_rows(group_by(records, "persona_id"), "persona_id")
    surface_rows = _build_group_rows(
        group_by(records, "evaluation_surface"),
        "evaluation_surface",
    )

    _write_json(summary_output, overall)
    _write_json(model_output, model_rows)
    _write_json(persona_output, persona_rows)
    _write_json(surface_output, surface_rows)
    _write_markdown_report(
        report_output,
        overall=overall,
        model_rows=model_rows,
        persona_rows=persona_rows,
        surface_rows=surface_rows,
    )

    print(summary_output)
    print(model_output)
    print(persona_output)
    print(surface_output)
    print(report_output)


if __name__ == "__main__":
    main()
