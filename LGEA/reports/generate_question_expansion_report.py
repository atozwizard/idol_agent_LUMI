from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

INPUT_PATH = Path("LGEA/data/questions/stress_expanded_questions.json")


def _load_payload(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    from LGEA.reports.batching import resolve_report_output

    payload = _load_payload(INPUT_PATH)
    items = payload.get("items", [])
    lines = [
        "# LGEA 질문 확장 보고서",
        "",
        f"- 확장 모드: `{payload.get('expansion_mode', '(없음)')}`",
        f"- 생성 모델: `{payload.get('generated_by', '(없음)')}`",
        f"- 부모 질문 수: {len(items)}",
        f"- 실패 항목 수: {payload.get('failure_count', 0)}",
        "",
    ]

    for item in items:
        lines.extend(
            [
                f"## {item['parent_question_id']}",
                "",
                f"- 카테고리: `{item.get('category') or '(없음)'}`",
                f"- 위험 라벨: `{item.get('risk_label') or '(없음)'}`",
                f"- 평가 표면: `{item.get('evaluation_surface') or '(없음)'}`",
                f"- 평가 목적: {item.get('evaluation_goal') or '(없음)'}",
                f"- 상태: `{item.get('status', '(없음)')}`",
                f"- 오류: {item.get('error', '(없음)')}",
                "",
            ]
        )
        for idx, variant in enumerate(item.get("variants", []), start=1):
            lines.extend(
                [
                    f"### variant {idx}",
                    "",
                    f"- variant_id: `{variant.get('variant_id', '(없음)')}`",
                    f"- variant_strategy: `{variant.get('variant_strategy', '(없음)')}`",
                    f"- difficulty_level: `{variant.get('difficulty_level', '(없음)')}`",
                    f"- escalation_level: `{variant.get('escalation_level', '(없음)')}`",
                    f"- review_status: `{variant.get('review_status', '(없음)')}`",
                    f"- attack_hypothesis: {variant.get('attack_hypothesis', '(없음)')}",
                    "",
                    variant.get("variant_prompt", "(없음)"),
                    "",
                ]
            )

    output_path = resolve_report_output("question_expansion_report_ko.md")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
