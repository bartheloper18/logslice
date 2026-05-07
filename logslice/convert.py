"""Convert log lines between formats (e.g. JSON <-> key=value <-> plain)."""
from __future__ import annotations

import json
from typing import Iterable, Iterator, Optional


_SUPPORTED = ("json", "kv", "plain")


def _to_dict(line: str) -> Optional[dict]:
    """Best-effort parse of a log line into a dict."""
    line = line.rstrip("\n")
    # Try JSON first
    try:
        obj = json.loads(line)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass
    # Try key=value
    pairs: dict = {}
    for token in line.split():
        if "=" in token:
            k, _, v = token.partition("=")
            pairs[k] = v.strip('"')
    if pairs:
        return pairs
    return None


def convert_line(line: str, target: str) -> str:
    """Convert *line* to *target* format ('json', 'kv', or 'plain')."""
    if target not in _SUPPORTED:
        raise ValueError(f"Unsupported target format: {target!r}. Choose from {_SUPPORTED}")

    raw = line.rstrip("\n")
    data = _to_dict(raw)

    if data is None:
        # Cannot parse — return as-is for plain, wrap for others
        if target == "plain":
            return raw + "\n"
        if target == "json":
            return json.dumps({"message": raw}) + "\n"
        if target == "kv":
            return f'message="{raw}"\n'

    if target == "json":
        return json.dumps(data) + "\n"
    if target == "kv":
        parts = []
        for k, v in data.items():
            v_str = str(v)
            parts.append(f'{k}="{v_str}"' if " " in v_str else f"{k}={v_str}")
        return " ".join(parts) + "\n"
    # plain: join values
    return " ".join(str(v) for v in data.values()) + "\n"


def convert_lines(lines: Iterable[str], target: str) -> Iterator[str]:
    """Yield converted lines."""
    for line in lines:
        yield convert_line(line, target)


def convert_file(path: str, target: str, out) -> int:
    """Convert *path* to *target* format, writing to *out*. Returns line count."""
    count = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for converted in convert_lines(fh, target):
            out.write(converted)
            count += 1
    return count
