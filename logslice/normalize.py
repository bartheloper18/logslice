"""Normalize log lines to a consistent format."""

from __future__ import annotations

import json
import re
from typing import IO, Iterator, Optional

# Matches common key=value or key="value" pairs
_KV_RE = re.compile(r'(\w+)=(?:"([^"]*)"|([^\s,]*))')


def normalize_line(line: str, target: str = "json") -> str:
    """Normalize a single log line to *target* format.

    Supported targets: ``json``, ``kv``.
    Lines that cannot be parsed are returned unchanged.
    """
    stripped = line.rstrip("\n")
    suffix = "\n" if line.endswith("\n") else ""

    fields = _parse_fields(stripped)
    if fields is None:
        return line

    if target == "json":
        result = json.dumps(fields, separators=(",", ":"))
    elif target == "kv":
        parts = []
        for k, v in fields.items():
            if " " in str(v) or "=" in str(v):
                parts.append(f'{k}="{v}"')
            else:
                parts.append(f"{k}={v}")
        result = " ".join(parts)
    else:
        raise ValueError(f"Unknown target format: {target!r}")

    return result + suffix


def _parse_fields(text: str) -> Optional[dict]:
    """Try to extract a field dict from *text*.

    Tries JSON first, then key=value pairs.
    Returns None when neither succeeds or the result is empty.
    """
    # Attempt JSON
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass

    # Attempt key=value
    fields = {}
    for m in _KV_RE.finditer(text):
        key = m.group(1)
        value = m.group(2) if m.group(2) is not None else m.group(3)
        fields[key] = value

    return fields if fields else None


def normalize_lines(
    lines: Iterator[str], target: str = "json"
) -> Iterator[str]:
    """Yield normalized versions of *lines*."""
    for line in lines:
        yield normalize_line(line, target=target)


def normalize_file(
    src: IO[str], dest: IO[str], target: str = "json"
) -> int:
    """Read lines from *src*, normalize them, write to *dest*.

    Returns the number of lines written.
    """
    count = 0
    for line in normalize_lines(src, target=target):
        dest.write(line)
        count += 1
    return count
