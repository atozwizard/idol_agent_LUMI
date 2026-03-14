from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import httpx

from LGEA.runner.target_client import _resolve_api_key

DEFAULT_CONFIG_PATH = Path("LGEA/configs/llm_ops.json")


@dataclass(frozen=True)
class SolarOpsModelConfig:
    model_id: str
    model_name: str
    api_base: str
    api_key_env: str
    timeout_seconds: int
    notes: str


class SolarOpsRegistry:
    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.judge_model = SolarOpsModelConfig(**payload["judge_model"])
        self.expander_model = SolarOpsModelConfig(**payload["expander_model"])


class SolarOpsClient:
    def __init__(self, registry: SolarOpsRegistry | None = None):
        self.registry = registry or SolarOpsRegistry()

    async def judge(self, *, user_prompt: str, system_prompt: str) -> dict:
        return await self._invoke_json(
            model=self.registry.judge_model,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )

    async def expand(self, *, user_prompt: str, system_prompt: str) -> dict:
        return await self._invoke_json(
            model=self.registry.expander_model,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
        )

    async def _invoke_json(
        self,
        *,
        model: SolarOpsModelConfig,
        user_prompt: str,
        system_prompt: str,
    ) -> dict:
        api_key = _resolve_api_key(model.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key: {model.api_key_env}")

        url = model.api_base.rstrip("/") + "/chat/completions"
        payload = {
            "model": model.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=model.timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("Model response was not a JSON object.")
        return parsed
