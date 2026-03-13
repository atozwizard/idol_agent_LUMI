from __future__ import annotations

import json
from pathlib import Path

SCORED_RESULTS_PATH = Path("LGEA/data/judge/scored_results.jsonl")
MATRIX_PATH = Path("LGEA/data/runs/experiment_matrix.json")
OUTPUT_JSONL_PATH = Path("LGEA/data/reports/conversation_log.jsonl")
OUTPUT_MD_PATH = Path("LGEA/reports/conversation_log_ko.md")


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    scored_rows = _read_jsonl(SCORED_RESULTS_PATH)
    matrix_rows = {row["run_id"]: row for row in _read_json(MATRIX_PATH)}

    conversations: list[dict] = []
    for row in scored_rows:
        matrix_row = matrix_rows.get(row["run_id"], {})
        prompt_text = row.get("prompt_text") or matrix_row.get("prompt")
        if not prompt_text and not row.get("response_text"):
            continue
        conversations.append(
            {
                "run_id": row["run_id"],
                "model_id": row["model_id"],
                "persona_id": row["persona_id"],
                "question_id": row["question_id"],
                "attack_type": row["attack_type"],
                "status": row["status"],
                "judge_status": row["judge_status"],
                "judge_rating": row["judge_rating"],
                "judge_score": row["judge_score"],
                "question_text": prompt_text,
                "system_prompt": row.get("system_prompt"),
                "answer_text": row.get("response_text"),
                "judge_reason": row["judge_reason"],
            }
        )

    OUTPUT_JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSONL_PATH.open("w", encoding="utf-8") as file:
        for row in conversations:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

    lines = [
        "# LGEA 질문-응답 로그",
        "",
        "실험별 질문과 모델 응답을 기록한 보고서입니다.",
        "",
    ]
    for idx, row in enumerate(conversations, start=1):
        lines.extend(
            [
                f"## {idx}. {row['run_id']}",
                "",
                f"- 모델: `{row['model_id']}`",
                f"- 페르소나: `{row['persona_id']}`",
                f"- 질문 ID: `{row['question_id']}`",
                f"- 공격 유형: `{row['attack_type']}`",
                f"- 실행 상태: `{row['status']}`",
                f"- 채점 상태: `{row['judge_status']}`",
                f"- 채점 결과: `{row['judge_rating']}` / 점수 `{row['judge_score']}`",
                f"- 채점 근거: {row['judge_reason']}",
                "",
                "질문:",
                "",
                row["question_text"] or "(질문 기록 없음)",
                "",
                "응답:",
                "",
                row["answer_text"] or "(응답 기록 없음)",
                "",
            ]
        )

    OUTPUT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT_JSONL_PATH)
    print(OUTPUT_MD_PATH)


if __name__ == "__main__":
    main()
