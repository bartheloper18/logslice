"""Count occurrences of field values or pattern matches across log lines."""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Iterable, Iterator


def _parse_fields(line: str) -> dict | None:
    """Return a dict of fields parsed from JSON or key=value line."""
    stripped = line.strip()
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass
    kv: dict = {}
    for token in re.findall(r'(\w+)=("[^"]*"|\S+)', stripped):
        key, val = token
        kv[key] = val.strip('"')
    return kv if kv else None


def count_by_field(
    lines: Iterable[str],
    field: str,
) -> Counter:
    """Count occurrences of each distinct value for *field* across *lines*."""
    counter: Counter = Counter()
    for line in lines:
        fields = _parse_fields(line)
        if fields and field in fields:
            counter[str(fields[field])] += 1
    return counter


def count_by_pattern(
    lines: Iterable[str],
    pattern: str,
    ignore_case: bool = False,
) -> Counter:
    """Count how many times each distinct captured group (or full match) appears."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled = re.compile(pattern, flags)
    counter: Counter = Counter()
    for line in lines:
        for match in compiled.finditer(line):
            key = match.group(1) if match.lastindex else match.group(0)
            counter[key] += 1
    return counter


def format_count(counter: Counter, top: int | None = None) -> Iterator[str]:
    """Yield formatted 'count\tvalue' lines sorted by descending count."""
    most_common = counter.most_common(top) if top else counter.most_common()
    for value, cnt in most_common:
        yield f"{cnt}\t{value}\n"


def count_file(
    path: str,
    field: str | None = None,
    pattern: str | None = None,
    ignore_case: bool = False,
    top: int | None = None,
) -> Iterator[str]:
    """Open *path* and yield formatted count lines."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    if field:
        counter = count_by_field(lines, field)
    elif pattern:
        counter = count_by_pattern(lines, pattern, ignore_case=ignore_case)
    else:
        counter = Counter(line.strip() for line in lines if line.strip())
    yield from format_count(counter, top=top)
