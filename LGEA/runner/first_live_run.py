from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_READINESS_PATH = Path("LGEA/data/runs/live_run_readiness.json")
DEFAULT_PROBE_PATH = Path("LGEA/data/runs/provider_probe.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the smallest safe LGEA live-run workflow."
    )
    parser.add_argument("--model-id", default="upstage-solar")
    parser.add_argument("--persona-id", default="drug")
    parser.add_argument("--question-id", default="baseline-001")
    parser.add_argument("--max-runs", type=int, default=1)
    return parser.parse_args()


def _run_command(command: list[str]) -> None:
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()

    _run_command([sys.executable, "LGEA/runner/live_run_check.py"])
    readiness = _load_json(DEFAULT_READINESS_PATH)
    if readiness.get("ready_model_count", 0) <= 0:
        raise SystemExit("No ready model is available for a live run.")

    _run_command([sys.executable, "LGEA/runner/provider_probe.py"])
    probe = _load_json(DEFAULT_PROBE_PATH)
    target_probe = next(
        (
            item
            for item in probe.get("models", [])
            if item.get("model_id") == args.model_id
        ),
        None,
    )
    if not target_probe:
        raise SystemExit(f"Probe result missing for model_id={args.model_id}")
    if target_probe.get("probe_status") != "reachable":
        raise SystemExit(
            f"Provider endpoint is not reachable for {args.model_id}: "
            f"{target_probe.get('error', target_probe.get('probe_status'))}"
        )

    _run_command(
        [
            sys.executable,
            "LGEA/runner/runner.py",
            "--execute-live",
            "--only-models",
            args.model_id,
            "--only-personas",
            args.persona_id,
            "--only-questions",
            args.question_id,
            "--max-runs",
            str(args.max_runs),
        ]
    )


if __name__ == "__main__":
    main()
