from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class LogTarget:
    folder: str
    prefix: str
    title: str


LOG_TARGETS = {
    "chat": LogTarget(
        folder="chat_logs",
        prefix="chatlog",
        title="LGEA Chat Log",
    ),
    "plan": LogTarget(
        folder="plans",
        prefix="plan",
        title="LGEA Plan",
    ),
    "progress": LogTarget(
        folder="progress",
        prefix="progress",
        title="LGEA Progress",
    ),
}


def build_file_path(log_type: str, now: datetime) -> Path:
    target = LOG_TARGETS[log_type]
    file_name = f"{target.prefix}_{now.strftime('%Y-%m-%d')}.md"
    return BASE_DIR / target.folder / file_name


def ensure_file(log_type: str, now: datetime) -> Path:
    path = build_file_path(log_type, now)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        target = LOG_TARGETS[log_type]
        header = [
            f"# {target.title}",
            "",
            f"- Date: {now.strftime('%Y-%m-%d')}",
            f"- Created At: {now.strftime('%H:%M:%S')}",
            "",
        ]
        path.write_text("\n".join(header), encoding="utf-8")

    return path


def append_entry(log_type: str, title: str, content: str, now: datetime) -> Path:
    path = ensure_file(log_type, now)
    entry = [
        f"## {now.strftime('%H:%M:%S')} | {title}",
        "",
        content.strip(),
        "",
    ]
    with path.open("a", encoding="utf-8") as file:
        file.write("\n".join(entry))
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or append LGEA chat/plan/progress documents by date."
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=sorted(LOG_TARGETS.keys()),
        help="Document type to write.",
    )
    parser.add_argument("--title", required=True, help="Entry title.")
    parser.add_argument("--content", required=True, help="Entry content.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    now = datetime.now()
    path = append_entry(
        log_type=args.type,
        title=args.title,
        content=args.content,
        now=now,
    )
    print(path)


if __name__ == "__main__":
    main()
