from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CROSS_SURFACE_PATH = Path("LGEA/data/analysis/cross_surface_summary.json")
COMPARATIVE_PATH = Path("LGEA/data/analysis/comparative_stats.json")


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    from LGEA.reports.batching import resolve_report_output

    cross_surface = _load_json(CROSS_SURFACE_PATH)
    comparative = _load_json(COMPARATIVE_PATH)
    summary = cross_surface.get("summary", {})
    sections = comparative.get("sections", [])

    lines = [
        "# AI Guardrail 발표자료",
        "",
        "## 1. 왜 이 프로젝트를 기획했는가",
        "",
        "기존 챗봇 평가는 최종 응답만 보고 끝나는 경우가 많다. 그러나 실제 서비스는 router, rag, tool, response-layer 같은 내부 표면을 거치며, guardrail 붕괴는 종단 응답 이전에도 발생할 수 있다. 이 프로젝트는 최종 응답만으로는 보이지 않는 내부 취약 지점을 함께 관찰하기 위해 기획되었다.",
        "",
        "---",
        "",
        "## 2. 무엇을 위해 하는가",
        "",
        "이 프로젝트의 목적은 LUMI의 어뷰즈 대응 성능을 질문-응답 수준에서 재현 가능하게 측정하고, 종단 응답과 내부 surface를 같은 질문셋으로 비교하는 것이다. 이를 통해 단순히 안전/비안전을 판정하는 수준을 넘어서, 어느 층위에서 guardrail이 유지되거나 흔들리는지를 분석한다.",
        "",
        "---",
        "",
        "## 3. 어떤 의미가 있는가",
        "",
        "이 프로젝트는 서비스형 LLM 시스템을 다층적으로 평가하는 실험 프레임워크라는 의미가 있다. 결과적으로 최종 사용자에게는 안전해 보이더라도 내부 response-layer, router, tool, rag에서 어떤 불안정성이 있는지 보여줄 수 있고, 이는 모델 선택, 라우팅 설계, 안전성 검증 체계 개선의 근거가 된다.",
        "",
        "---",
        "",
        "## 4. 어떻게 평가하는가",
        "",
        "- 공통 baseline 질문셋으로 FastAPI 종단 평가 수행",
        "- 같은 질문셋으로 내부 service surface 점검 수행",
        "- 질문, 응답, 메타데이터, 판정 결과를 모두 저장",
        "- cross-surface analysis와 comparative analysis로 비교",
        "",
        "---",
        "",
        "## 5. 현재 파일럿 결과",
        "",
        f"- 전체 비교 질문 수: {summary.get('total_questions', 0)}",
        f"- 어뷰즈 질문 수: {summary.get('abuse_question_count', 0)}",
        f"- FastAPI 결과 수: {summary.get('fastapi_question_count', 0)}",
        f"- 내부 response-layer 결과 수: {summary.get('service_response_question_count', 0)}",
        f"- 불일치 건수: {summary.get('mismatch_count', 0)}",
        "",
        "---",
        "",
        "## 6. 현재까지 읽을 수 있는 의미",
        "",
        "FastAPI 종단 응답은 상대적으로 방어적으로 보이지만, 내부 response-layer는 더 모호하거나 경계적인 응답을 보일 수 있다. 또한 router/tool/rag 단계의 실패는 단순 기능 오류가 아니라 안전성 결과에 영향을 미치는 구조적 리스크로 해석할 수 있다.",
        "",
        "---",
        "",
        "## 7. 통계 비교 상태",
        "",
    ]

    for section in sections:
        lines.append(f"### {section['title']}")
        lines.append("")
        lines.append(section.get("interpretation", ""))
        lines.append("")
        for comparison in section.get("comparisons", []):
            lines.append(
                "- "
                f"{comparison['metric_name']}: "
                f"diff={comparison['rate_diff']}, "
                f"p={comparison['p_value']}, "
                f"enough_samples={comparison['enough_samples']}"
            )
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## 8. 결론",
            "",
            "이 프로젝트는 AI guardrail을 단일 응답 수준이 아니라 서비스 다층 구조에서 평가하기 위한 연구 인프라다. 현재 결과는 파일럿 단계이지만, 다층 평가 프레임워크 제안과 내부 취약 지점 관찰이라는 점에서 발표와 논문 초안의 근거가 된다.",
            "",
        ]
    )

    output_path = resolve_report_output("presentation_guardrail_ko.md")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
