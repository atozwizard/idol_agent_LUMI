from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

PERSONA_IDS = ("drug", "bomb", "adult")
PROMPT_TARGETS = ("ROUTER_PROMPT", "RESPONSE_PROMPT", "RAG_RESPONSE_PROMPT")
SOURCE_FILE = "app/core/prompts.py"
PROMPT_PATTERN = re.compile(
    r'(?P<name>[A-Z_]+)\s*=\s*"""(?P<body>.*?)"""',
    re.DOTALL,
)


@dataclass(frozen=True)
class PromptDelta:
    target: str
    baseline_line_count: int
    persona_line_count: int
    baseline_bullet_count: int
    persona_bullet_count: int
    redacted_preview: str


@dataclass(frozen=True)
class NormalizedPersona:
    persona_id: str
    source_branch: str
    source_file: str
    prompt_targets: list[str]
    injection_style: list[str]
    response_policy_shift: str
    deltas: list[PromptDelta]


def _count_lines(text: str) -> int:
    return len(text.strip().splitlines())


def _count_bullets(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip().startswith("- "))


def _redacted_preview(text: str, max_lines: int = 8) -> str:
    preview = "\n".join(text.strip().splitlines()[:max_lines])
    for term in ("마약", "폭탄", "섹스", "살인"):
        preview = preview.replace(term, "[REDACTED]")
    return preview


def _policy_shift(persona_id: str) -> str:
    return {
        "drug": "Current Lumi persona is evaluated against drug-related abuse questions that test refusal, escalation handling, and safe alternatives.",
        "bomb": "Current Lumi persona is evaluated against bomb-related abuse questions that test boundary keeping and non-procedural safety responses.",
        "adult": "Current Lumi persona is evaluated against adult-content abuse questions that test boundary setting and safe redirection.",
    }[persona_id]


def _load_current_prompts(repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or Path(__file__).resolve().parents[2]
    text = (root / SOURCE_FILE).read_text(encoding="utf-8")
    prompts: dict[str, str] = {}
    for match in PROMPT_PATTERN.finditer(text):
        prompts[match.group("name")] = match.group("body").strip()
    return prompts


def build_registry(repo_root: Path | None = None) -> list[NormalizedPersona]:
    prompt_map = _load_current_prompts(repo_root=repo_root)

    deltas = [
        PromptDelta(
            target=name,
            baseline_line_count=_count_lines(body),
            persona_line_count=_count_lines(body),
            baseline_bullet_count=_count_bullets(body),
            persona_bullet_count=_count_bullets(body),
            redacted_preview=_redacted_preview(body),
        )
        for name, body in prompt_map.items()
    ]

    registry: list[NormalizedPersona] = []
    for persona_id in PERSONA_IDS:
        registry.append(
            NormalizedPersona(
                persona_id=persona_id,
                source_branch="current_branch",
                source_file=SOURCE_FILE,
                prompt_targets=list(PROMPT_TARGETS),
                injection_style=["current persona fixed", "question-set variation"],
                response_policy_shift=_policy_shift(persona_id),
                deltas=deltas,
            )
        )
    return registry


def export_registry(output_path: Path, repo_root: Path | None = None) -> Path:
    registry = build_registry(repo_root=repo_root)
    payload = [asdict(persona) for persona in registry]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path
