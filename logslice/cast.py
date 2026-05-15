"""Field type casting for structured log lines."""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Iterator, Optional


_CASTERS = {
    "int": int,
    "float": float,
    "bool": lambda v: v.lower() in ("true", "1", "yes"),
    "str": str,
}


def cast_value(value: str, typename: str) -> Any:
    """Cast *value* to *typename*; raise ValueError on failure."""
    if typename not in _CASTERS:
        raise ValueError(f"Unknown type '{typename}'. Choose from: {', '.join(_CASTERS)}")
    try:
        return _CASTERS[typename](value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Cannot cast {value!r} to {typename}: {exc}") from exc


def _parse_fields(line: str) -> Optional[Dict[str, Any]]:
    """Return parsed JSON dict or None."""
    stripped = line.rstrip("\n")
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def cast_line(line: str, field: str, typename: str) -> str:
    """Return *line* with *field* cast to *typename* (JSON lines only).

    Lines that are not valid JSON objects, or that do not contain *field*,
    are returned unchanged.
    """
    trail = "\n" if line.endswith("\n") else ""
    fields = _parse_fields(line)
    if fields is None or field not in fields:
        return line
    raw = fields[field]
    try:
        fields[field] = cast_value(str(raw), typename)
    except ValueError:
        return line
    return json.dumps(fields, separators=(",", ":")) + trail


def cast_lines(
    lines: Iterable[str],
    field: str,
    typename: str,
) -> Iterator[str]:
    """Yield lines with *field* cast to *typename*."""
    for line in lines:
        yield cast_line(line, field, typename)


def cast_file(path: str, field: str, typename: str) -> Iterator[str]:
    """Open *path* and yield cast lines."""
    with open(path, encoding="utf-8") as fh:
        yield from cast_lines(fh, field, typename)
