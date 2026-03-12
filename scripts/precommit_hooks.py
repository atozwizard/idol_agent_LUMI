from __future__ import annotations

import ast
import sys
from pathlib import Path


def iter_paths(paths: list[str]) -> list[Path]:
    return [Path(path) for path in paths if Path(path).is_file()]


def read_text_if_utf8(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def eof_fixer(paths: list[str]) -> int:
    changed = False
    for path in iter_paths(paths):
        text = read_text_if_utf8(path)
        if text is None:
            continue
        fixed = text.rstrip("\r\n")
        fixed = fixed + ("\n" if fixed else "")
        if fixed != text:
            path.write_text(fixed, encoding="utf-8", newline="")
            print(f"Fixing {path}")
            changed = True
    return 1 if changed else 0


def trailing_whitespace(paths: list[str]) -> int:
    changed = False
    for path in iter_paths(paths):
        original = read_text_if_utf8(path)
        if original is None:
            continue
        lines = original.splitlines(keepends=True)
        fixed_lines: list[str] = []
        for line in lines:
            line_ending = ""
            if line.endswith("\r\n"):
                line_ending = "\r\n"
                body = line[:-2]
            elif line.endswith("\n"):
                line_ending = "\n"
                body = line[:-1]
            else:
                body = line
            fixed_lines.append(body.rstrip(" \t") + line_ending)
        fixed = "".join(fixed_lines)
        if fixed != original:
            path.write_text(fixed, encoding="utf-8", newline="")
            print(f"Fixing {path}")
            changed = True
    return 1 if changed else 0


def check_yaml(paths: list[str]) -> int:
    try:
        import yaml
    except ImportError:
        print("PyYAML is required for check-yaml", file=sys.stderr)
        return 1

    failed = False
    for path in iter_paths(paths):
        try:
            content = read_text_if_utf8(path)
            if content is None:
                print(f"{path}: not valid UTF-8 text", file=sys.stderr)
                failed = True
                continue
            yaml.safe_load(content)
        except Exception as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


def check_added_large_files(paths: list[str], maxkb: int) -> int:
    failed = False
    max_bytes = maxkb * 1024
    for path in iter_paths(paths):
        size = path.stat().st_size
        if size > max_bytes:
            print(f"{path}: exceeds {maxkb} KB ({size} bytes)", file=sys.stderr)
            failed = True
    return 1 if failed else 0


def check_ast(paths: list[str]) -> int:
    failed = False
    for path in iter_paths(paths):
        content = read_text_if_utf8(path)
        if content is None:
            print(f"{path}: not valid UTF-8 python source", file=sys.stderr)
            failed = True
            continue
        try:
            ast.parse(content, filename=str(path))
        except SyntaxError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


def debug_statements(paths: list[str]) -> int:
    failed = False
    for path in iter_paths(paths):
        content = read_text_if_utf8(path)
        if content is None:
            print(f"{path}: not valid UTF-8 python source", file=sys.stderr)
            failed = True
            continue
        tree = ast.parse(content, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "breakpoint":
                    print(f"{path}:{node.lineno}: breakpoint() found", file=sys.stderr)
                    failed = True
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr == "set_trace"
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "pdb"
                ):
                    print(
                        f"{path}:{node.lineno}: pdb.set_trace() found", file=sys.stderr
                    )
                    failed = True
    return 1 if failed else 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: precommit_hooks.py <command> [paths...]", file=sys.stderr)
        return 2

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "eof-fixer":
        return eof_fixer(args)
    if command == "trailing-whitespace":
        return trailing_whitespace(args)
    if command == "check-yaml":
        return check_yaml(args)
    if command == "check-added-large-files":
        maxkb = 1000
        paths: list[str] = []
        for arg in args:
            if arg.startswith("--maxkb="):
                maxkb = int(arg.split("=", 1)[1])
            else:
                paths.append(arg)
        return check_added_large_files(paths, maxkb)
    if command == "check-ast":
        return check_ast(args)
    if command == "debug-statements":
        return debug_statements(args)

    print(f"Unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
