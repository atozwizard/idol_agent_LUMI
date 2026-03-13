from __future__ import annotations

from LGEA.prompts.adult_prompt import get_prompt_bundle as get_adult_prompt_bundle
from LGEA.prompts.bomb_prompt import get_prompt_bundle as get_bomb_prompt_bundle
from LGEA.prompts.branch_prompt_loader import PromptBundle, load_prompt_bundle
from LGEA.prompts.drug_prompt import get_prompt_bundle as get_drug_prompt_bundle

PROMPT_VARIANTS = {
    "plain": lambda: load_prompt_bundle(test_type="plain"),
    "drug": get_drug_prompt_bundle,
    "bomb": get_bomb_prompt_bundle,
    "adult": get_adult_prompt_bundle,
}


def select_prompt_bundle(test_type: str) -> PromptBundle:
    normalized = test_type.strip().lower()
    try:
        loader = PROMPT_VARIANTS[normalized]
    except KeyError as exc:
        allowed = ", ".join(sorted(PROMPT_VARIANTS))
        raise ValueError(
            f"Unsupported test_type={test_type!r}. Allowed: {allowed}"
        ) from exc
    return loader()
