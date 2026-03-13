from __future__ import annotations

import json
from pathlib import Path

SUMMARY_PATH = Path("LGEA/data/analysis/summary.json")
MODEL_SUMMARY_PATH = Path("LGEA/data/analysis/model_summary.json")
PERSONA_SUMMARY_PATH = Path("LGEA/data/analysis/persona_summary.json")
SURFACE_SUMMARY_PATH = Path("LGEA/data/analysis/surface_summary.json")
SCORED_RESULTS_PATH = Path("LGEA/data/judge/scored_results.jsonl")
OUTPUT_PATH = Path("LGEA/reports/live_run_report_ko.md")
CONVERSATION_LOG_PATH = Path("LGEA/data/reports/conversation_log.jsonl")


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _latest_scored_record(records: list[dict]) -> dict | None:
    scored = [record for record in records if record.get("judge_status") == "scored"]
    if not scored:
        return None
    return scored[-1]


def _read_conversation_rows() -> list[dict]:
    if not CONVERSATION_LOG_PATH.exists():
        return []
    return _read_jsonl(CONVERSATION_LOG_PATH)


def main() -> None:
    summary = _read_json(SUMMARY_PATH)
    model_rows = _read_json(MODEL_SUMMARY_PATH)
    persona_rows = _read_json(PERSONA_SUMMARY_PATH)
    surface_rows = _read_json(SURFACE_SUMMARY_PATH)
    scored_results = _read_jsonl(SCORED_RESULTS_PATH)
    conversation_rows = _read_conversation_rows()
    latest = _latest_scored_record(scored_results)

    lines = [
        "# LGEA 1차 Live Run 한국어 보고서",
        "",
        "## 1. 개요",
        "",
        "- 본 보고서는 현재 저장소에서 확보된 1차 live run 결과를 기준으로 작성했습니다.",
        "- 평가 범위는 응답층, RAG, 도구, 라우터를 포함하는 다층 분석 구조를 기준으로 정리합니다.",
        "",
        "## 2. 현재 집계 결과",
        "",
        f"- 전체 실행 수: {summary['total_runs']}",
        f"- 채점 완료 수: {summary['scored_runs']}",
        f"- 거부 응답 수: {summary['refused_runs']}",
        f"- 위험 응답 수: {summary['unsafe_runs']}",
        f"- 거부율: {summary['refusal_rate']}",
        f"- 공격 성공률: {summary['attack_success_rate']}",
        "",
        "## 3. 모델별 요약",
        "",
        "| 모델 | 전체 실행수 | 채점 수 | 거부 수 | 위험 응답 수 | 거부율 | 공격 성공률 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in model_rows:
        lines.append(
            f"| {row['model_id']} | {row['total_runs']} | {row['scored_runs']} | "
            f"{row['refused_runs']} | {row['unsafe_runs']} | "
            f"{row['refusal_rate']} | {row['attack_success_rate']} |"
        )

    lines.extend(
        [
            "",
            "## 4. 카테고리별 요약",
            "",
            "| 카테고리 | 전체 실행수 | 채점 수 | 거부 수 | 위험 응답 수 | 거부율 | 공격 성공률 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in persona_rows:
        lines.append(
            f"| {row['persona_id']} | {row['total_runs']} | {row['scored_runs']} | "
            f"{row['refused_runs']} | {row['unsafe_runs']} | "
            f"{row['refusal_rate']} | {row['attack_success_rate']} |"
        )

    lines.extend(
        [
            "",
            "## 5. 평가 대상별 요약",
            "",
            "| 평가 대상 | 전체 실행수 | 채점 수 | 거부 수 | 위험 응답 수 | 거부율 | 공격 성공률 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in surface_rows:
        lines.append(
            f"| {row['evaluation_surface']} | {row['total_runs']} | {row['scored_runs']} | "
            f"{row['refused_runs']} | {row['unsafe_runs']} | "
            f"{row['refusal_rate']} | {row['attack_success_rate']} |"
        )

    lines.extend(
        [
            "",
            "## 6. 1차 live run 대표 사례",
            "",
        ]
    )
    if latest is None:
        lines.extend(
            [
                "- 아직 채점 완료된 live 응답이 없습니다.",
                "",
            ]
        )
    else:
        excerpt = (latest.get("response_text") or "").replace("\n", " ").strip()
        excerpt = excerpt[:220] + ("..." if len(excerpt) > 220 else "")
        lines.extend(
            [
                f"- run_id: `{latest['run_id']}`",
                f"- 모델: `{latest['model_id']}`",
                f"- 카테고리: `{latest['persona_id']}`",
                f"- 질문 ID: `{latest['question_id']}`",
                f"- 평가 대상: `{latest.get('evaluation_surface', 'response-layer')}`",
                f"- 상태: `{latest['status']}`",
                f"- 채점 결과: `{latest['judge_rating']}` / 점수 `{latest['judge_score']}`",
                f"- 채점 근거: {latest['judge_reason']}",
                f"- 응답 발췌: {excerpt}",
                "",
            ]
        )

    lines.extend(
        [
            "## 7. 질문-응답 기록",
            "",
        ]
    )
    if not conversation_rows:
        lines.extend(["- 아직 내보낸 질문-응답 로그가 없습니다.", ""])
    else:
        for idx, row in enumerate(conversation_rows, start=1):
            lines.extend(
                [
                    f"### {idx}. {row['run_id']}",
                    "",
                    f"- 모델: `{row['model_id']}`",
                    f"- 카테고리: `{row['persona_id']}`",
                    f"- 질문 ID: `{row['question_id']}`",
                    f"- 평가 대상: `{row.get('evaluation_surface', 'response-layer')}`",
                    f"- 채점 결과: `{row['judge_rating']}` / 점수 `{row['judge_score']}`",
                    "",
                    "질문:",
                    "",
                    row.get("question_text") or "(질문 기록 없음)",
                    "",
                    "응답:",
                    "",
                    row.get("answer_text") or "(응답 기록 없음)",
                    "",
                ]
            )

    lines.extend(
        [
            "## 8. 해석",
            "",
            "- 현재 확보된 1차 live run 1건에서는 모델이 위험 요청에 대해 정책 준수형 거부 응답을 보였습니다.",
            "- 따라서 현재 표본 기준 공격 성공 사례는 관찰되지 않았습니다.",
            "- 다만 표본 수가 매우 적으므로 모델 간 일반화된 결론을 내리기에는 이릅니다.",
            "",
            "## 9. 다음 단계",
            "",
            "- `google-gemini` 1건 이상 추가 실행",
            "- `upstage-solar`에 대해 다른 질문 ID로 반복 실행",
            "- 표본 확대 후 통계 요약 재생성",
            "",
        ]
    )

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
