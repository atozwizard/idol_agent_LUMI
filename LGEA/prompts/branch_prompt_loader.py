from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SOURCE = "current_branch:app/core/prompts.py"
SOURCE_FILE = "app/core/prompts.py"
PROMPT_PATTERN = re.compile(
    r'(?P<name>[A-Z_]+)\s*=\s*"""(?P<body>.*?)"""',
    re.DOTALL,
)


@dataclass(frozen=True)
class PromptBundle:
    source: str
    test_type: str
    router_prompt: str
    response_prompt: str
    rag_response_prompt: str


def load_prompt_bundle(*, test_type: str = "plain") -> PromptBundle:
    normalized = test_type.strip().lower()
    root = Path(__file__).resolve().parents[2]
    text = (root / SOURCE_FILE).read_text(encoding="utf-8")
    prompts: dict[str, str] = {}
    for match in PROMPT_PATTERN.finditer(text):
        prompts[match.group("name")] = match.group("body").strip()
    return PromptBundle(
        source=DEFAULT_SOURCE,
        test_type=normalized,
        router_prompt=prompts["ROUTER_PROMPT"],
        response_prompt=prompts["RESPONSE_PROMPT"],
        rag_response_prompt=prompts["RAG_RESPONSE_PROMPT"],
    )
