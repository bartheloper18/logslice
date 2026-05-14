"""Column alignment for structured log fields."""

from __future__ import annotations

import json
from typing import Iterable, Iterator, List, Optional


def _parse_fields(line: str) -> Optional[dict]:
    """Try JSON then key=value parsing; return None if neither matches."""
    line = line.rstrip("\n")
    try:
        obj = json.loads(line)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass
    fields: dict = {}
    for token in line.split():
        if "=" in token:
            k, _, v = token.partition("=")
            fields[k] = v.strip('"')
    return fields or None


def _pad(value: str, width: int) -> str:
    return value.ljust(width)


def align_lines(
    lines: Iterable[str],
    keys: List[str],
    separator: str = "  ",
    missing: str = "-",
) -> Iterator[str]:
    """Emit lines with requested fields aligned into fixed-width columns.

    The column width for each key is determined by the widest value seen
    across *all* input lines, so the input is buffered before output.
    """
    buffered: List[Optional[dict]] = []
    raw: List[str] = []
    widths: dict[str, int] = {k: len(k) for k in keys}

    for line in lines:
        raw.append(line)
        fields = _parse_fields(line)
        buffered.append(fields)
        if fields is not None:
            for k in keys:
                val = str(fields.get(k, missing))
                if len(val) > widths[k]:
                    widths[k] = len(val)

    for line, fields in zip(raw, buffered):
        if fields is None:
            yield line if line.endswith("\n") else line + "\n"
            continue
        parts = []
        for k in keys:
            header_or_val = str(fields.get(k, missing))
            parts.append(_pad(header_or_val, widths[k]))
        yield separator.join(parts) + "\n"


def align_file(
    path: str,
    keys: List[str],
    separator: str = "  ",
    missing: str = "-",
) -> Iterator[str]:
    """Open *path* and yield aligned lines."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        yield from align_lines(fh, keys, separator=separator, missing=missing)
