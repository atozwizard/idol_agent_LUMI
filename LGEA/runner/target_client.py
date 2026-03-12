from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TargetModelConfig:
    model_id: str
    provider: str
    enabled: bool
    notes: str


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
                "notes": model.notes,
            }
            for model in self._models
        ]
