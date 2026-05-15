"""Column extraction and formatting for structured log lines."""

from __future__ import annotations

import json
import re
from typing import Iterable, Iterator, List, Optional


_KV_RE = re.compile(r'(\w+)=("[^"]*"|\S+)')


def _parse_fields(line: str) -> Optional[dict]:
    """Return a field dict from JSON or key=value line, else None."""
    stripped = line.strip()
    if stripped.startswith("{"):
        try:
            obj = json.loads(stripped)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    pairs = _KV_RE.findall(line)
    if pairs:
        return {k: v.strip('"') for k, v in pairs}
    return None


def extract_columns(line: str, keys: List[str], missing: str = "") -> List[str]:
    """Return a list of values for *keys* extracted from *line*."""
    fields = _parse_fields(line)
    if fields is None:
        return [missing] * len(keys)
    return [str(fields.get(k, missing)) for k in keys]


def _column_widths(rows: List[List[str]]) -> List[int]:
    if not rows:
        return []
    return [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]


def format_columns(
    lines: Iterable[str],
    keys: List[str],
    separator: str = "  ",
    missing: str = "-",
    header: bool = True,
) -> Iterator[str]:
    """Yield formatted, aligned column output for *keys* extracted from *lines*."""
    rows: List[List[str]] = []
    for line in lines:
        rows.append(extract_columns(line, keys, missing=missing))

    if not rows:
        return

    if header:
        rows.insert(0, [k.upper() for k in keys])

    widths = _column_widths(rows)

    for row in rows:
        yield separator.join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip() + "\n"


def column_file(path: str, keys: List[str], **kwargs) -> Iterator[str]:
    """Open *path* and yield formatted column output."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        yield from format_columns(fh, keys, **kwargs)
