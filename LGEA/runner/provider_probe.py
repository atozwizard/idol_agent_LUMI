from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_OUTPUT_PATH = Path("LGEA/data/runs/provider_probe.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe provider endpoints for basic LGEA live-run connectivity."
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Path to the provider probe JSON report.",
    )
    return parser.parse_args()


async def main() -> None:
    from LGEA.runner.target_client import TargetClientRegistry, _resolve_api_key

    args = parse_args()
    output_path = Path(args.output)
    registry = TargetClientRegistry()
    report_models: list[dict[str, object]] = []

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for model in registry.list_models(enabled_only=False):
            has_api_key = bool(_resolve_api_key(model.api_key_env))
            url = model.api_base.rstrip("/") + "/models"
            probe_result: dict[str, object] = {
                "model_id": model.model_id,
                "provider": model.provider,
                "enabled": model.enabled,
                "api_base": model.api_base,
                "probe_url": url,
                "has_api_key": has_api_key,
            }
            try:
                response = await client.get(url)
                probe_result["probe_status"] = "reachable"
                probe_result["http_status"] = response.status_code
            except httpx.TimeoutException as exc:
                probe_result["probe_status"] = "timeout"
                probe_result["error"] = f"{type(exc).__name__}: {exc}"
            except httpx.HTTPError as exc:
                probe_result["probe_status"] = "transport_error"
                probe_result["error"] = f"{type(exc).__name__}: {exc}"
            report_models.append(probe_result)

    output = {"models": report_models}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
