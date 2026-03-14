from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_FASTAPI_INPUT = Path("LGEA/data/runs/fastapi_live_results.jsonl")
DEFAULT_SERVICE_INPUT = Path("LGEA/data/runs/service_surface_results.jsonl")
DEFAULT_JSON_OUTPUT = Path("LGEA/data/runs/repetition_plan.json")
DEFAULT_MARKDOWN_OUTPUT = Path("LGEA/reports/repetition_plan_ko.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a repeat-run plan for statistically stronger LGEA claims."
    )
    parser.add_argument("--fastapi-input", default=str(DEFAULT_FASTAPI_INPUT))
    parser.add_argument("--service-input", default=str(DEFAULT_SERVICE_INPUT))
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--markdown-output", default=str(DEFAULT_MARKDOWN_OUTPUT))
    parser.add_argument("--target-scored-runs", type=int, default=10)
    return parser.parse_args()


def _load_scored_records(path: Path) -> list[dict]:
    from LGEA.judge.rubric import load_rubric, score_response
    from LGEA.judge.storage import load_final_run_records

    rubric = load_rubric()
    rubric_version = int(rubric.get("version", 1))
    rows: list[dict] = []
    for record in load_final_run_records(path):
        decision = score_response(
            run_id=record.run_id,
            status=record.status,
            mode=record.mode,
            response_text=record.response_text,
            rubric_version=rubric_version,
        )
        rows.append(
            {
                "run_id": record.run_id,
                "question_id": record.question_id,
                "persona_id": record.persona_id,
                "evaluation_surface": record.evaluation_surface,
                "judge_status": decision.judge_status,
            }
        )
    return rows


def _count_scored(rows: list[dict], *, fastapi_mode: bool) -> dict[str, int]:
    counts = {
        "abuse_response_layer": 0,
        "response_probe": 0,
        "router_probe": 0,
        "rag_probe": 0,
        "tool_probe": 0,
    }
    for row in rows:
        if row["judge_status"] != "scored":
            continue
        question_id = row["question_id"]
        surface = row["evaluation_surface"]
        if (
            question_id.startswith(("drug-", "bomb-", "adult-"))
            and surface == "response-layer"
        ):
            counts["abuse_response_layer"] += 1
        elif question_id.startswith("response-"):
            counts["response_probe"] += 1
        elif question_id.startswith("router-"):
            counts["router_probe"] += 1
        elif question_id.startswith("rag-"):
            counts["rag_probe"] += 1
        elif question_id.startswith("tool-"):
            counts["tool_probe"] += 1
    if fastapi_mode:
        counts.pop("router_probe", None)
        counts.pop("rag_probe", None)
        counts.pop("tool_probe", None)
        counts.pop("response_probe", None)
    return counts


def _build_payload(
    fastapi_rows: list[dict],
    service_rows: list[dict],
    *,
    target_scored_runs: int,
) -> dict:
    fastapi_counts = _count_scored(fastapi_rows, fastapi_mode=True)
    service_counts = _count_scored(service_rows, fastapi_mode=False)

    fastapi_gap = max(0, target_scored_runs - fastapi_counts["abuse_response_layer"])
    service_gap = max(0, target_scored_runs - service_counts["abuse_response_layer"])
    recommended_full_batches = max(
        1 if fastapi_gap > 0 else 0,
        1 if service_gap > 0 else 0,
    )

    return {
        "target_scored_runs_per_group": target_scored_runs,
        "current_fastapi_counts": fastapi_counts,
        "current_service_counts": service_counts,
        "gaps": {
            "fastapi_abuse_response_layer_gap": fastapi_gap,
            "service_abuse_response_layer_gap": service_gap,
        },
        "recommendation": {
            "minimum_additional_full_fastapi_batches": recommended_full_batches,
            "rationale": (
                "공유 baseline 질문셋 전체를 한 번 더 실행하면 FastAPI와 내부 response-layer의 "
                "어뷰즈 scored run 수가 모두 10건 이상으로 올라간다."
            ),
            "commands": [
                "python LGEA/runner/fastapi_live_run.py --base-url http://127.0.0.1:8000",
                "python LGEA/analysis/cross_surface_analysis.py",
                "python LGEA/analysis/comparative_analysis.py",
            ],
        },
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_markdown(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    recommendation = payload["recommendation"]
    fastapi_counts = payload["current_fastapi_counts"]
    service_counts = payload["current_service_counts"]
    gaps = payload["gaps"]

    lines = [
        "# LGEA 반복 실행 계획",
        "",
        "통계적 우월성 주장 가능 수준에 도달하기 위해 필요한 최소 반복 실행 계획이다.",
        "",
        "## 현재 scored run 상태",
        "",
        f"- FastAPI 어뷰즈 response-layer scored run 수: {fastapi_counts['abuse_response_layer']}",
        f"- 내부 response-layer 어뷰즈 scored run 수: {service_counts['abuse_response_layer']}",
        f"- 내부 response probe scored run 수: {service_counts['response_probe']}",
        f"- 내부 router probe scored run 수: {service_counts['router_probe']}",
        f"- 내부 rag probe scored run 수: {service_counts['rag_probe']}",
        f"- 내부 tool probe scored run 수: {service_counts['tool_probe']}",
        "",
        "## 최소 추가 필요량",
        "",
        f"- FastAPI 어뷰즈 response-layer 추가 필요 수: {gaps['fastapi_abuse_response_layer_gap']}",
        f"- 내부 response-layer 어뷰즈 추가 필요 수: {gaps['service_abuse_response_layer_gap']}",
        "",
        "## 권장 실행",
        "",
        f"- 최소 추가 full batch 수: {recommendation['minimum_additional_full_fastapi_batches']}",
        f"- 근거: {recommendation['rationale']}",
        "",
        "권장 명령:",
        "",
    ]
    for command in recommendation["commands"]:
        lines.append(f"- `{command}`")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    from LGEA.reports.batching import resolve_report_output

    args = parse_args()
    fastapi_rows = _load_scored_records(Path(args.fastapi_input))
    service_rows = _load_scored_records(Path(args.service_input))
    payload = _build_payload(
        fastapi_rows,
        service_rows,
        target_scored_runs=args.target_scored_runs,
    )
    _write_json(Path(args.json_output), payload)
    markdown_output = Path(args.markdown_output)
    if markdown_output == DEFAULT_MARKDOWN_OUTPUT:
        markdown_output = resolve_report_output("repetition_plan_ko.md")
    _write_markdown(markdown_output, payload)
    print(args.json_output)
    print(markdown_output)


if __name__ == "__main__":
    main()
