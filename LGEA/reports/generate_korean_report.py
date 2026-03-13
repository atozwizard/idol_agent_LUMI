from __future__ import annotations

import json
from pathlib import Path

SUMMARY_PATH = Path("LGEA/data/analysis/summary.json")
MODEL_SUMMARY_PATH = Path("LGEA/data/analysis/model_summary.json")
PERSONA_SUMMARY_PATH = Path("LGEA/data/analysis/persona_summary.json")
SCORED_RESULTS_PATH = Path("LGEA/data/judge/scored_results.jsonl")
OUTPUT_PATH = Path("LGEA/reports/live_run_report_ko.md")


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


def main() -> None:
    summary = _read_json(SUMMARY_PATH)
    model_rows = _read_json(MODEL_SUMMARY_PATH)
    persona_rows = _read_json(PERSONA_SUMMARY_PATH)
    scored_results = _read_jsonl(SCORED_RESULTS_PATH)
    latest = _latest_scored_record(scored_results)

    lines = [
        "# LGEA 1차 Live Run 한국어 보고서",
        "",
        "## 1. 개요",
        "",
        "- 본 보고서는 현재 저장소에서 확보된 1차 live run 결과를 기준으로 작성했습니다.",
        "- 평가 범위는 모델 API의 응답층이며, RAG와 도구 호출은 제외합니다.",
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
            "## 4. 페르소나별 요약",
            "",
            "| 페르소나 | 전체 실행수 | 채점 수 | 거부 수 | 위험 응답 수 | 거부율 | 공격 성공률 |",
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
            "## 5. 1차 live run 대표 사례",
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
                f"- 페르소나: `{latest['persona_id']}`",
                f"- 질문 ID: `{latest['question_id']}`",
                f"- 상태: `{latest['status']}`",
                f"- 채점 결과: `{latest['judge_rating']}` / 점수 `{latest['judge_score']}`",
                f"- 채점 근거: {latest['judge_reason']}",
                f"- 응답 발췌: {excerpt}",
                "",
            ]
        )

    lines.extend(
        [
            "## 6. 해석",
            "",
            "- 현재 확보된 1차 live run 1건에서는 모델이 위험 요청에 대해 정책 준수형 거부 응답을 보였습니다.",
            "- 따라서 현재 표본 기준 공격 성공 사례는 관찰되지 않았습니다.",
            "- 다만 표본 수가 매우 적으므로 모델 간 일반화된 결론을 내리기에는 이릅니다.",
            "",
            "## 7. 다음 단계",
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
