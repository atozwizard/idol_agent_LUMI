from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_OUTPUT = Path("LGEA/data/baseline/baseline_plan.json")
DEFAULT_REGISTRY_OUTPUT = Path("LGEA/data/personas/normalized_registry.json")


@dataclass(frozen=True)
class BaselineRunPlan:
    created_at: str
    baseline_branch: str
    evaluation_scope: str
    prompt_targets: list[str]
    persona_count: int
    personas: list[dict]
    notes: list[str]


def build_baseline_plan(repo_root: Path | None = None) -> BaselineRunPlan:
    from LGEA.personas.registry import build_registry

    root = repo_root or Path(__file__).resolve().parents[2]
    registry = build_registry(repo_root=root)
    return BaselineRunPlan(
        created_at=datetime.now().isoformat(timespec="seconds"),
        baseline_branch="dev",
        evaluation_scope="response-layer-only",
        prompt_targets=["RESPONSE_PROMPT"],
        persona_count=len(registry),
        personas=[
            {
                "persona_id": persona.persona_id,
                "source_branch": persona.source_branch,
                "injection_style": persona.injection_style,
                "response_policy_shift": persona.response_policy_shift,
            }
            for persona in registry
        ],
        notes=[
            "This artifact is a baseline execution plan only. It does not execute external model APIs.",
            "RAG prompts are excluded from the active evaluation scope.",
            "Branch prompt contents are redacted at the registry layer for safer handling.",
        ],
    )


def export_baseline_plan(output_path: Path, repo_root: Path | None = None) -> Path:
    plan = build_baseline_plan(repo_root=repo_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(asdict(plan), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build LGEA baseline plan artifacts.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path for the generated baseline plan JSON.",
    )
    parser.add_argument(
        "--registry-output",
        default=str(DEFAULT_REGISTRY_OUTPUT),
        help="Path for the generated normalized persona registry JSON.",
    )
    return parser.parse_args()


def main() -> None:
    from LGEA.personas.registry import export_registry

    args = parse_args()
    root = PROJECT_ROOT
    registry_path = export_registry(Path(args.registry_output), repo_root=root)
    plan_path = export_baseline_plan(Path(args.output), repo_root=root)
    print(registry_path)
    print(plan_path)


if __name__ == "__main__":
    main()
