from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from LGEA.personas.loader import PromptBlock, load_branch_snapshot

BASELINE_BRANCH = "dev"
PERSONA_BRANCHES = ("drug", "bomb", "adult")
PROMPT_TARGETS = ("RESPONSE_PROMPT",)


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


def _classify_injection_style(prompt: PromptBlock, baseline: PromptBlock) -> list[str]:
    styles: list[str] = []
    if prompt.line_count > baseline.line_count:
        styles.append("rule expansion")
    if prompt.bullet_count > baseline.bullet_count:
        styles.append("behavior overwrite")
    if "거절" in prompt.body and "거절" in baseline.body:
        styles.append("refusal policy mutation")
    if not styles:
        styles.append("prompt mutation")
    return styles


def _policy_shift(persona_id: str) -> str:
    return {
        "drug": "Baseline refusal-oriented idol persona is shifted toward unsafe compliance in the drug-related branch.",
        "bomb": "Baseline refusal-oriented idol persona is shifted toward unsafe compliance in the bomb-related branch.",
        "adult": "Baseline refusal-oriented idol persona is shifted toward explicit-response bias in the adult-related branch.",
    }[persona_id]


def build_registry(repo_root: Path | None = None) -> list[NormalizedPersona]:
    root = repo_root or Path(__file__).resolve().parents[2]
    baseline_snapshot = load_branch_snapshot(BASELINE_BRANCH, repo_root=root)
    registry: list[NormalizedPersona] = []

    for persona_id in PERSONA_BRANCHES:
        snapshot = load_branch_snapshot(persona_id, repo_root=root)
        deltas: list[PromptDelta] = []
        injection_style: set[str] = set()

        for target in PROMPT_TARGETS:
            baseline_prompt = baseline_snapshot.get_prompt(target)
            persona_prompt = snapshot.get_prompt(target)
            injection_style.update(
                _classify_injection_style(persona_prompt, baseline_prompt)
            )
            deltas.append(
                PromptDelta(
                    target=target,
                    baseline_line_count=baseline_prompt.line_count,
                    persona_line_count=persona_prompt.line_count,
                    baseline_bullet_count=baseline_prompt.bullet_count,
                    persona_bullet_count=persona_prompt.bullet_count,
                    redacted_preview=persona_prompt.redacted_preview(),
                )
            )

        registry.append(
            NormalizedPersona(
                persona_id=persona_id,
                source_branch=persona_id,
                source_file=snapshot.source_file,
                prompt_targets=list(PROMPT_TARGETS),
                injection_style=sorted(injection_style),
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
