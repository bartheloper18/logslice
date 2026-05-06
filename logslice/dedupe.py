"""Deduplication of repeated log lines."""

from __future__ import annotations

from collections import OrderedDict
from typing import Iterable, Iterator


def dedupe_lines(
    lines: Iterable[str],
    *,
    consecutive_only: bool = False,
    max_cache: int = 1024,
) -> Iterator[str]:
    """Yield unique log lines, suppressing duplicates.

    Args:
        lines: Iterable of raw log line strings.
        consecutive_only: When True, only suppress *adjacent* duplicate lines
            (faster; suitable for sorted logs). When False, suppress any
            previously seen line within the rolling *max_cache* window.
        max_cache: Maximum number of distinct lines to remember when
            ``consecutive_only`` is False. Oldest entries are evicted first.

    Yields:
        Deduplicated log lines (trailing newline preserved if present).
    """
    if consecutive_only:
        yield from _dedupe_consecutive(lines)
    else:
        yield from _dedupe_windowed(lines, max_cache)


def _dedupe_consecutive(lines: Iterable[str]) -> Iterator[str]:
    prev: str | None = None
    for line in lines:
        key = line.rstrip("\n")
        if key != prev:
            yield line
            prev = key


def _dedupe_windowed(lines: Iterable[str], max_cache: int) -> Iterator[str]:
    seen: OrderedDict[str, None] = OrderedDict()
    for line in lines:
        key = line.rstrip("\n")
        if key in seen:
            continue
        if len(seen) >= max_cache:
            seen.popitem(last=False)
        seen[key] = None
        yield line


def dedupe_file(
    path: str,
    *,
    consecutive_only: bool = False,
    max_cache: int = 1024,
    encoding: str = "utf-8",
) -> Iterator[str]:
    """Open *path* and yield deduplicated lines."""
    with open(path, encoding=encoding, errors="replace") as fh:
        yield from dedupe_lines(
            fh,
            consecutive_only=consecutive_only,
            max_cache=max_cache,
        )
