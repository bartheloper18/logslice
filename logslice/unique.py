"""Unique field value extraction and deduplication by structured field."""

from __future__ import annotations

import json
from typing import Iterable, Iterator, Optional


def _parse_fields(line: str) -> Optional[dict]:
    """Try JSON then key=value parsing; return dict or None."""
    stripped = line.strip()
    if stripped.startswith("{"):
        try:
            obj = json.loads(stripped)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    fields: dict = {}
    for token in stripped.split():
        if "=" in token:
            k, _, v = token.partition("=")
            fields[k.strip()] = v.strip('"').strip()
    return fields if fields else None


def unique_lines(
    lines: Iterable[str],
    field: Optional[str] = None,
    ignore_case: bool = False,
) -> Iterator[str]:
    """Yield lines whose key value (or full text) has not been seen before.

    Args:
        lines: Input log lines.
        field: Structured field name to deduplicate on.  When *None* the
               entire stripped line is used as the key.
        ignore_case: Normalise string keys to lower-case before comparison.
    """
    seen: set = set()
    for line in lines:
        if field is not None:
            parsed = _parse_fields(line)
            raw_key = parsed.get(field) if parsed else None
            if raw_key is None:
                # Lines that lack the field are always emitted.
                yield line
                continue
            key = str(raw_key).lower() if ignore_case else str(raw_key)
        else:
            key = line.strip().lower() if ignore_case else line.strip()

        if key not in seen:
            seen.add(key)
            yield line


def unique_values(
    lines: Iterable[str],
    field: str,
    ignore_case: bool = False,
) -> Iterator[str]:
    """Yield the distinct values of *field* across all structured lines."""
    seen: set = set()
    for line in lines:
        parsed = _parse_fields(line)
        if not parsed:
            continue
        raw = parsed.get(field)
        if raw is None:
            continue
        key = str(raw).lower() if ignore_case else str(raw)
        if key not in seen:
            seen.add(key)
            yield str(raw)


def unique_file(
    path: str,
    field: Optional[str] = None,
    ignore_case: bool = False,
) -> Iterator[str]:
    """Open *path* and apply :func:`unique_lines`."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        yield from unique_lines(fh, field=field, ignore_case=ignore_case)
