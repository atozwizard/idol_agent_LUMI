from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExperimentRunItem:
    run_id: str
    model_id: str
    persona_id: str
    question_id: str
    evaluation_surface: str
    attack_type: str
    category: str
    prompt: str


def load_plan(plan_path: Path) -> dict:
    return json.loads(plan_path.read_text(encoding="utf-8"))


def build_experiment_matrix(
    *,
    plan_path: Path,
    include_disabled_models: bool = False,
) -> list[ExperimentRunItem]:
    payload = load_plan(plan_path)
    models = payload.get("models", [])
    personas = payload.get("personas", [])
    questions = payload.get("questions", [])
    matrix: list[ExperimentRunItem] = []

    for model in models:
        if not include_disabled_models and not model.get("enabled", False):
            continue
        for persona in personas:
            for question in questions:
                question_persona = question.get("persona_id")
                if question_persona and question_persona != persona["persona_id"]:
                    continue
                run_id = (
                    f"{model['model_id']}__{persona['persona_id']}__"
                    f"{question['question_id']}"
                )
                matrix.append(
                    ExperimentRunItem(
                        run_id=run_id,
                        model_id=model["model_id"],
                        persona_id=persona["persona_id"],
                        question_id=question["question_id"],
                        evaluation_surface=question.get(
                            "evaluation_surface",
                            "response-layer",
                        ),
                        attack_type=question["attack_type"],
                        category=question.get("category", persona["persona_id"]),
                        prompt=question["prompt"],
                    )
                )
    return matrix


def export_experiment_matrix(
    *,
    plan_path: Path,
    output_path: Path,
    include_disabled_models: bool = False,
) -> Path:
    matrix = build_experiment_matrix(
        plan_path=plan_path,
        include_disabled_models=include_disabled_models,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([asdict(item) for item in matrix], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path
