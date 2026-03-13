from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import httpx


@dataclass(frozen=True)
class TargetModelConfig:
    model_id: str
    provider: str
    enabled: bool
    model_name: str
    api_base: str
    api_key_env: str
    timeout_seconds: int
    notes: str


@dataclass(frozen=True)
class TargetInvocationResult:
    run_id: str
    model_id: str
    provider: str
    status: str
    response_text: str
    used_model_name: str
    mode: str
    notes: str | None = None


def _stringify_content(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        return "\n".join(chunks)
    return ""


class TargetClientRegistry:
    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path("LGEA/configs/models.json")
        self._models = self._load_models()

    def _load_models(self) -> list[TargetModelConfig]:
        payload = json.loads(self.config_path.read_text(encoding="utf-8"))
        return [
            TargetModelConfig(
                model_id=item["model_id"],
                provider=item["provider"],
                enabled=item["enabled"],
                model_name=item.get("model_name", ""),
                api_base=item.get("api_base", ""),
                api_key_env=item.get("api_key_env", ""),
                timeout_seconds=item.get("timeout_seconds", 30),
                notes=item["notes"],
            )
            for item in payload.get("models", [])
        ]

    def list_models(self, enabled_only: bool = False) -> list[TargetModelConfig]:
        if enabled_only:
            return [model for model in self._models if model.enabled]
        return list(self._models)

    def export_summary(self) -> list[dict[str, str | bool]]:
        return [
            {
                "model_id": model.model_id,
                "provider": model.provider,
                "enabled": model.enabled,
                "model_name": model.model_name,
                "api_base": model.api_base,
                "api_key_env": model.api_key_env,
                "timeout_seconds": model.timeout_seconds,
                "notes": model.notes,
            }
            for model in self._models
        ]

    def get_model(self, model_id: str) -> TargetModelConfig:
        for model in self._models:
            if model.model_id == model_id:
                return model
        raise KeyError(f"Unknown model_id: {model_id}")


class TargetClient:
    def __init__(self, registry: TargetClientRegistry | None = None):
        self.registry = registry or TargetClientRegistry()

    async def invoke(
        self,
        *,
        run_id: str,
        model_id: str,
        prompt: str,
        system_prompt: str | None = None,
        execute_live: bool = False,
    ) -> TargetInvocationResult:
        model = self.registry.get_model(model_id)
        if not execute_live:
            return self._dry_run_result(run_id=run_id, model=model, prompt=prompt)
        return await self._live_invoke(
            run_id=run_id,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
        )

    def _dry_run_result(
        self,
        *,
        run_id: str,
        model: TargetModelConfig,
        prompt: str,
    ) -> TargetInvocationResult:
        preview = prompt[:80].replace("\n", " ")
        return TargetInvocationResult(
            run_id=run_id,
            model_id=model.model_id,
            provider=model.provider,
            status="dry_run_completed",
            response_text=f"[dry-run] {model.model_id} would receive: {preview}",
            used_model_name=model.model_name or model.model_id,
            mode="dry-run",
            notes="External model API call was not executed.",
        )

    async def _live_invoke(
        self,
        *,
        run_id: str,
        model: TargetModelConfig,
        prompt: str,
        system_prompt: str | None,
    ) -> TargetInvocationResult:
        if not model.enabled:
            return TargetInvocationResult(
                run_id=run_id,
                model_id=model.model_id,
                provider=model.provider,
                status="skipped_disabled_model",
                response_text="",
                used_model_name=model.model_name or model.model_id,
                mode="live",
                notes="Model is disabled in LGEA/configs/models.json.",
            )

        if not model.model_name:
            return TargetInvocationResult(
                run_id=run_id,
                model_id=model.model_id,
                provider=model.provider,
                status="skipped_missing_model_name",
                response_text="",
                used_model_name=model.model_id,
                mode="live",
                notes="model_name is empty in LGEA/configs/models.json.",
            )

        api_key = os.getenv(model.api_key_env, "")
        if not api_key:
            return TargetInvocationResult(
                run_id=run_id,
                model_id=model.model_id,
                provider=model.provider,
                status="skipped_missing_api_key",
                response_text="",
                used_model_name=model.model_name,
                mode="live",
                notes=f"Missing environment variable: {model.api_key_env}",
            )

        url = model.api_base.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": model.model_name,
            "messages": messages,
        }
        try:
            async with httpx.AsyncClient(timeout=model.timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException:
            return TargetInvocationResult(
                run_id=run_id,
                model_id=model.model_id,
                provider=model.provider,
                status="failed_timeout",
                response_text="",
                used_model_name=model.model_name,
                mode="live",
                notes=f"Timed out after {model.timeout_seconds} seconds.",
            )
        except httpx.HTTPStatusError as exc:
            response_preview = (
                exc.response.text[:300] if exc.response is not None else ""
            )
            return TargetInvocationResult(
                run_id=run_id,
                model_id=model.model_id,
                provider=model.provider,
                status="failed_http_error",
                response_text="",
                used_model_name=model.model_name,
                mode="live",
                notes=f"HTTP {exc.response.status_code}: {response_preview}",
            )
        except httpx.HTTPError as exc:
            return TargetInvocationResult(
                run_id=run_id,
                model_id=model.model_id,
                provider=model.provider,
                status="failed_transport_error",
                response_text="",
                used_model_name=model.model_name,
                mode="live",
                notes=str(exc),
            )
        except Exception as exc:
            return TargetInvocationResult(
                run_id=run_id,
                model_id=model.model_id,
                provider=model.provider,
                status="failed_unexpected_error",
                response_text="",
                used_model_name=model.model_name,
                mode="live",
                notes=str(exc),
            )

        content = _stringify_content(
            data.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
        return TargetInvocationResult(
            run_id=run_id,
            model_id=model.model_id,
            provider=model.provider,
            status="completed",
            response_text=content,
            used_model_name=model.model_name,
            mode="live",
            notes=None,
        )
