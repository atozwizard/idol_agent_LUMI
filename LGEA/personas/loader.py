from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

PROMPT_PATTERN = re.compile(
    r'(?P<name>[A-Z_]+)\s*=\s*"""(?P<body>.*?)"""',
    re.DOTALL,
)

REDACTED_TERMS = (
    "마약",
    "폭탄",
    "섹스",
    "자지",
    "보지",
    "살인",
    "정액",
    "펠라",
)


@dataclass(frozen=True)
class PromptBlock:
    name: str
    body: str

    @property
    def line_count(self) -> int:
        return len(self.body.splitlines())

    @property
    def bullet_count(self) -> int:
        return sum(
            1 for line in self.body.splitlines() if line.strip().startswith("- ")
        )

    def redacted_preview(self, max_lines: int = 8) -> str:
        lines = self.body.splitlines()[:max_lines]
        preview = "\n".join(lines)
        for term in REDACTED_TERMS:
            preview = preview.replace(term, "[REDACTED]")
        return preview


@dataclass(frozen=True)
class BranchPromptSnapshot:
    branch: str
    source_file: str
    prompts: dict[str, PromptBlock]

    def get_prompt(self, name: str) -> PromptBlock:
        try:
            return self.prompts[name]
        except KeyError as exc:
            raise KeyError(
                f"{name} not found in {self.branch}:{self.source_file}"
            ) from exc


def _git_show(branch: str, source_file: str, cwd: Path) -> str:
    completed = subprocess.run(
        ["git", "show", f"{branch}:{source_file}"],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return completed.stdout


def _extract_prompt_blocks(text: str) -> dict[str, PromptBlock]:
    prompts: dict[str, PromptBlock] = {}
    for match in PROMPT_PATTERN.finditer(text):
        name = match.group("name")
        body = match.group("body").strip()
        prompts[name] = PromptBlock(name=name, body=body)
    return prompts


def load_branch_snapshot(
    branch: str,
    source_file: str = "app/core/prompts.py",
    repo_root: Path | None = None,
) -> BranchPromptSnapshot:
    root = repo_root or Path(__file__).resolve().parents[2]
    text = _git_show(branch=branch, source_file=source_file, cwd=root)
    prompts = _extract_prompt_blocks(text)
    return BranchPromptSnapshot(branch=branch, source_file=source_file, prompts=prompts)
