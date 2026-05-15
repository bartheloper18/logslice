"""Flatten nested JSON log lines into dot-notation key-value pairs."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, Optional


def _flatten_dict(
    obj: Any,
    prefix: str = "",
    sep: str = ".",
) -> Dict[str, Any]:
    """Recursively flatten a nested dict into a single-level dict."""
    items: Dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}{sep}{key}" if prefix else key
            if isinstance(value, dict):
                items.update(_flatten_dict(value, full_key, sep))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    indexed_key = f"{full_key}{sep}{i}"
                    if isinstance(item, dict):
                        items.update(_flatten_dict(item, indexed_key, sep))
                    else:
                        items[indexed_key] = item
            else:
                items[full_key] = value
    return items


def flatten_line(line: str, sep: str = ".") -> str:
    """Flatten a single JSON log line.  Non-JSON lines are returned unchanged."""
    stripped = line.rstrip("\n")
    try:
        obj = json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        return line
    if not isinstance(obj, dict):
        return line
    flat = _flatten_dict(obj, sep=sep)
    suffix = "\n" if line.endswith("\n") else ""
    return json.dumps(flat, ensure_ascii=False) + suffix


def flatten_lines(
    lines: Iterator[str],
    sep: str = ".",
) -> Iterator[str]:
    """Yield flattened versions of each line."""
    for line in lines:
        yield flatten_line(line, sep=sep)


def flatten_file(path: str, sep: str = ".", out=None) -> None:
    """Read *path*, flatten every JSON line, write results to *out*."""
    import sys

    sink = out if out is not None else sys.stdout
    with open(path, "r", encoding="utf-8") as fh:
        for result in flatten_lines(fh, sep=sep):
            sink.write(result)
