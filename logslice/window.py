"""Sliding-window log extraction: return lines whose timestamps fall
within a relative time window ending now (or a given anchor)."""

from __future__ import annotations

import datetime
from typing import Iterable, Iterator, Optional

from logslice.parser import extract_timestamp


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def window_lines(
    lines: Iterable[str],
    seconds: float,
    anchor: Optional[datetime.datetime] = None,
) -> Iterator[str]:
    """Yield lines whose timestamp is within *seconds* before *anchor*.

    Lines with no parseable timestamp are always yielded.

    Args:
        lines:   Iterable of raw log lines.
        seconds: Width of the window in seconds (must be > 0).
        anchor:  Upper bound of the window (default: current UTC time).
    """
    if seconds <= 0:
        raise ValueError("seconds must be positive")

    end = anchor if anchor is not None else _utcnow()
    if end.tzinfo is None:
        end = end.replace(tzinfo=datetime.timezone.utc)
    start = end - datetime.timedelta(seconds=seconds)

    for line in lines:
        ts = extract_timestamp(line)
        if ts is None:
            yield line
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=datetime.timezone.utc)
        if start <= ts <= end:
            yield line


def window_file(
    path: str,
    seconds: float,
    anchor: Optional[datetime.datetime] = None,
    encoding: str = "utf-8",
) -> Iterator[str]:
    """Open *path* and yield lines within the time window."""
    with open(path, encoding=encoding, errors="replace") as fh:
        yield from window_lines(fh, seconds=seconds, anchor=anchor)
