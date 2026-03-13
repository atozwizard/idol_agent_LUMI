from __future__ import annotations

from LGEA.prompts.branch_prompt_loader import PromptBundle, load_prompt_bundle

TEST_TYPE = "bomb"


def get_prompt_bundle() -> PromptBundle:
    return load_prompt_bundle(test_type=TEST_TYPE)
