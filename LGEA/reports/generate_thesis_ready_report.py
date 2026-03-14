from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CROSS_SURFACE_PATH = Path("LGEA/data/analysis/cross_surface_summary.json")
COMPARATIVE_PATH = Path("LGEA/data/analysis/comparative_stats.json")
REPETITION_PLAN_PATH = Path("LGEA/data/runs/repetition_plan.json")
PAPER_CLAIMS_PATH = Path("LGEA/reports/paper_claims_ko.md")


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _surface_meaning_lines(cross_surface: dict) -> list[str]:
    rows = cross_surface.get("rows", [])
    router_failures = sum(
        1
        for row in rows
        if row.get("service_router")
        and row["service_router"].get("status") != "completed"
    )
    rag_failures = sum(
        1
        for row in rows
        if row.get("service_rag") and row["service_rag"].get("status") != "completed"
    )
    tool_failures = sum(
        1
        for row in rows
        if row.get("service_tool") and row["service_tool"].get("status") != "completed"
    )
    borderline_internal = sum(
        1 for row in rows if row.get("service_response_label") == "borderline"
    )
    safe_fastapi = sum(1 for row in rows if row.get("fastapi_label") == "safe")

    return [
        f"- `FastAPI 종단 응답`은 최종 사용자에게 노출되는 방어 결과이며, 현재 비교표에서 안전 판정은 {safe_fastapi}건이다.",
        f"- `response-layer`는 최종 문장 생성 품질을 보여주며, 현재 경계 판정은 {borderline_internal}건이다. 즉 내부 응답층이 얼마나 모호하거나 불안정한지 읽을 수 있다.",
        f"- `router`는 입력 분류와 경로 선택을 의미한다. 현재 비정상 router 결과는 {router_failures}건으로, 잘못된 분기가 후속 안전성 저하와 연결될 수 있다.",
        f"- `rag`는 검색 기반 정보 회수 안정성을 의미한다. 현재 비정상 RAG 결과는 {rag_failures}건으로, 검색 실패가 곧바로 응답 품질 저하로 이어질 수 있다.",
        f"- `tool`은 도구 호출 경로의 안전성과 기능 정상성을 의미한다. 현재 비정상 tool 결과는 {tool_failures}건으로, 기능 오류와 guardrail 실패를 함께 관찰해야 함을 보여준다.",
    ]


def main() -> None:
    from LGEA.reports.batching import resolve_report_output

    cross_surface = _load_json(CROSS_SURFACE_PATH)
    comparative = _load_json(COMPARATIVE_PATH)
    repetition = _load_json(REPETITION_PLAN_PATH)
    claims = _load_text(PAPER_CLAIMS_PATH)

    cross_summary = cross_surface.get("summary", {})
    sections = comparative.get("sections", [])
    recommendation = repetition.get("recommendation", {})

    lines = [
        "# LGEA 논문형 결과 요약",
        "",
        "이 문서는 현재 LGEA 산출물에서 바로 논문 초안으로 옮길 수 있는 수준의 결과 요약을 정리한다.",
        "",
        "## 다층 안전성 평가 프레임워크",
        "",
        "본 연구는 LUMI 서비스의 안전성을 FastAPI 최종 응답, 내부 `response-layer`, `router`, `rag`, `tool`로 분리 관찰하는 다층 평가 프레임워크를 구현한다.",
        "동일 baseline 질문셋을 종단 평가와 내부 surface 점검에 공통 적용하여 질문-응답-경로를 직접 비교할 수 있게 했다.",
        "",
        "## 파일럿 결과 요약",
        "",
        f"- 전체 비교 질문 수: {cross_summary.get('total_questions', 0)}",
        f"- 어뷰즈 질문 수: {cross_summary.get('abuse_question_count', 0)}",
        f"- FastAPI 결과가 있는 질문 수: {cross_summary.get('fastapi_question_count', 0)}",
        f"- 내부 response-layer 결과가 있는 질문 수: {cross_summary.get('service_response_question_count', 0)}",
        f"- FastAPI와 response-layer 정렬 일치 건수: {cross_summary.get('aligned_count', 0)}",
        f"- FastAPI와 response-layer 불일치 건수: {cross_summary.get('mismatch_count', 0)}",
        "",
        "현재 파일럿 결과에서는 FastAPI 최종 응답이 상대적으로 방어적이지만, 내부 response-layer에서는 경계적이거나 모호한 응답이 반복적으로 관찰된다.",
        "",
        "## 다층 질답 의미 분석",
        "",
        *_surface_meaning_lines(cross_surface),
        "",
        "## 통계 비교 결과",
        "",
    ]

    for section in sections:
        lines.append(f"### {section['title']}")
        lines.append("")
        lines.append(section["interpretation"])
        lines.append("")
        for comparison in section.get("comparisons", []):
            lines.append(
                "- "
                f"{comparison['metric_name']}: "
                f"{comparison['baseline_group']}={comparison['baseline']['rate']}, "
                f"{comparison['target_group']}={comparison['target']['rate']}, "
                f"diff={comparison['rate_diff']}, "
                f"p={comparison['p_value']}, "
                f"significant={comparison['significant']}, "
                f"enough_samples={comparison['enough_samples']}"
            )
        lines.append("")

    lines.extend(
        [
            "## 해석 범위",
            "",
            "현재 결과는 다층 프레임워크 제안과 파일럿 관찰을 뒷받침하지만, 통계적 우월성 주장은 아직 표본이 부족해 제한적이다.",
            "",
            "## 통계 주장 확장을 위한 최소 조건",
            "",
            f"- 권장 최소 추가 full batch 수: {recommendation.get('minimum_additional_full_fastapi_batches', 0)}",
            f"- 근거: {recommendation.get('rationale', '반복 실행 계획 필요')}",
            "",
            "## 논문 서술 초안",
            "",
            claims or "(논문 서술 초안 없음)",
            "",
        ]
    )

    output_path = resolve_report_output("thesis_ready_report_ko.md")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
