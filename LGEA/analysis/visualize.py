from __future__ import annotations


def render_markdown_table(rows: list[dict], headers: list[str]) -> str:
    if not rows:
        return "| No data |\n| --- |"

    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join("---" for _ in headers) + " |"
    body_lines = []
    for row in rows:
        body_lines.append(
            "| " + " | ".join(str(row.get(header, "")) for header in headers) + " |"
        )
    return "\n".join([header_line, separator_line, *body_lines])
