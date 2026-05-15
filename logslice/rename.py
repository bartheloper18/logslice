"""Rename / remap fields in structured log lines."""

from __future__ import annotations

import json
from typing import Dict, Iterable, Iterator, Optional


def _parse_fields(line: str) -> Optional[dict]:
    """Return a dict if the line is a JSON object, else None."""
    stripped = line.rstrip("\n")
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def _parse_kv(line: str) -> Optional[dict]:
    """Parse simple key=value (space-separated) lines."""
    parts = line.rstrip("\n").split()
    result: dict = {}
    for part in parts:
        if "=" in part:
            k, _, v = part.partition("=")
            result[k] = v
    return result if result else None


def rename_fields(line: str, mapping: Dict[str, str]) -> str:
    """Rename fields in *line* according to *mapping* (old_name -> new_name).

    Supports JSON-object lines and key=value lines.  Plain text lines are
    returned unchanged.
    """
    trailing_nl = line.endswith("\n")

    obj = _parse_fields(line)
    if obj is not None:
        renamed = {mapping.get(k, k): v for k, v in obj.items()}
        result = json.dumps(renamed, separators=(",", ":"))
        return result + "\n" if trailing_nl else result

    kv = _parse_kv(line)
    if kv is not None:
        parts = [f"{mapping.get(k, k)}={v}" for k, v in kv.items()]
        result = " ".join(parts)
        return result + "\n" if trailing_nl else result

    return line


def rename_lines(
    lines: Iterable[str], mapping: Dict[str, str]
) -> Iterator[str]:
    """Yield each line with fields renamed according to *mapping*."""
    for line in lines:
        yield rename_fields(line, mapping)


def rename_file(path: str, mapping: Dict[str, str], out) -> None:
    """Read *path*, rename fields, write results to *out* file-like object."""
    with open(path, "r", encoding="utf-8") as fh:
        for line in rename_lines(fh, mapping):
            out.write(line)
