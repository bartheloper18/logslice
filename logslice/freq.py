"""Frequency analysis: count how often each unique line (or field value) appears."""
from __future__ import annotations

import json
from collections import Counter
from typing import Iterable, Iterator, List, Optional, Tuple


def _parse_fields(line: str) -> Optional[dict]:
    """Return parsed dict for JSON or key=value lines, else None."""
    stripped = line.strip()
    if stripped.startswith("{"):
        try:
            obj = json.loads(stripped)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    if "=" in stripped:
        fields: dict = {}
        for token in stripped.split():
            if "=" in token:
                k, _, v = token.partition("=")
                fields[k] = v.strip('"')
        if fields:
            return fields
    return None


def freq_lines(
    lines: Iterable[str],
    field: Optional[str] = None,
    top: Optional[int] = None,
) -> List[Tuple[str, int]]:
    """Return (value, count) pairs sorted by descending frequency.

    If *field* is given, count occurrences of that field's value;
    otherwise count whole (stripped) lines.
    """
    counter: Counter = Counter()
    for line in lines:
        if field:
            parsed = _parse_fields(line)
            if parsed is None or field not in parsed:
                continue
            key = str(parsed[field])
        else:
            key = line.rstrip("\n")
        counter[key] += 1

    results = counter.most_common(top)
    return results


def format_freq(results: List[Tuple[str, int]], total: int) -> Iterator[str]:
    """Yield formatted lines: count, percentage, value."""
    width = len(str(max((c for _, c in results), default=0)))
    for value, count in results:
        pct = (count / total * 100) if total else 0.0
        yield f"{count:{width}d}  {pct:5.1f}%  {value}\n"


def freq_file(
    path: str,
    field: Optional[str] = None,
    top: Optional[int] = None,
    out=None,
) -> None:
    """Read *path*, compute frequency, write formatted results to *out*."""
    import sys

    out = out or sys.stdout
    with open(path, "r", errors="replace") as fh:
        lines = fh.readlines()
    results = freq_lines(lines, field=field, top=top)
    total = sum(c for _, c in results)
    for line in format_freq(results, total):
        out.write(line)
