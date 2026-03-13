from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_OUTPUT_PATH = Path("LGEA/data/runs/live_run_readiness.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate whether the LGEA workspace is ready for a first live run."
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Path to the readiness report JSON.",
    )
    return parser.parse_args()


def _load_env_file(path: Path = Path(".env")) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


ENV_FILE_VALUES = _load_env_file()


def _resolve_api_key(env_name: str) -> str:
    if not env_name:
        return ""
    env_value = os.getenv(env_name, "")
    if env_value:
        return env_value
    return ENV_FILE_VALUES.get(env_name, "")


def main() -> None:
    from LGEA.runner.target_client import TargetClientRegistry

    args = parse_args()
    output_path = Path(args.output)
    registry = TargetClientRegistry()

    models: list[dict[str, object]] = []
    ready_model_count = 0

    for model in registry.list_models(enabled_only=False):
        has_api_key = bool(_resolve_api_key(model.api_key_env))
        is_ready = bool(model.enabled and model.model_name and has_api_key)
        if is_ready:
            ready_model_count += 1
        models.append(
            {
                "model_id": model.model_id,
                "provider": model.provider,
                "enabled": model.enabled,
                "has_model_name": bool(model.model_name),
                "has_api_key": has_api_key,
                "api_key_env": model.api_key_env,
                "timeout_seconds": model.timeout_seconds,
                "is_ready": is_ready,
            }
        )

    report = {
        "status": "ready" if ready_model_count > 0 else "not_ready",
        "ready_model_count": ready_model_count,
        "models": models,
        "recommended_first_run": {
            "command": (
                "python LGEA/runner/runner.py --execute-live "
                "--only-models upstage-solar --only-personas drug "
                "--only-questions drug-001 --max-runs 1"
            ),
            "notes": "Use a single-model, single-category, single-question response-layer run before expanding to other surfaces.",
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    main()
