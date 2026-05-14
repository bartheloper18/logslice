"""Strip fields or prefixes from log lines."""

from __future__ import annotations

import json
import re
from typing import Iterable, Iterator, List, Optional


_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(line: str) -> str:
    """Remove ANSI colour escape sequences from *line*."""
    return _ANSI_ESCAPE.sub("", line)


def strip_fields(line: str, fields: List[str]) -> str:
    """Remove named keys from a JSON or key=value log line.

    For JSON lines the matching keys are deleted from the object.
    For key=value lines the matching ``key=value`` tokens are removed.
    Plain lines are returned unchanged.
    """
    stripped = line.rstrip("\n")
    nl = "\n" if line.endswith("\n") else ""

    # Try JSON first
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict):
            for f in fields:
                obj.pop(f, None)
            return json.dumps(obj) + nl
    except (json.JSONDecodeError, ValueError):
        pass

    # Try key=value
    if re.search(r"\w+=", stripped):
        for f in fields:
            # Match key=value or key="..."
            pattern = re.compile(
                r"(?:^|\s)" + re.escape(f) + r'=(?:"[^"]*"|\S*)'
            )
            stripped = pattern.sub("", stripped).strip()
        return stripped + nl

    return line


def strip_prefix(line: str, prefix: str) -> str:
    """Remove a literal *prefix* from the start of *line* (after whitespace)."""
    lstripped = line.lstrip()
    if lstripped.startswith(prefix):
        return lstripped[len(prefix):].lstrip()
    return line


def strip_lines(
    lines: Iterable[str],
    fields: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    ansi: bool = False,
) -> Iterator[str]:
    """Apply stripping operations to each line in *lines*."""
    for line in lines:
        if ansi:
            line = strip_ansi(line)
        if fields:
            line = strip_fields(line, fields)
        if prefix is not None:
            line = strip_prefix(line, prefix)
        yield line


def strip_file(
    path: str,
    fields: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    ansi: bool = False,
) -> Iterator[str]:
    """Open *path* and yield stripped lines."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        yield from strip_lines(fh, fields=fields, prefix=prefix, ansi=ansi)
