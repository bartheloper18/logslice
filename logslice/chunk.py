"""Split log lines into fixed-size or time-based chunks."""

from __future__ import annotations

import io
from typing import Iterable, Iterator, List, Optional

from logslice.parser import extract_timestamp


def chunk_by_count(lines: Iterable[str], size: int) -> Iterator[List[str]]:
    """Yield successive chunks of *size* lines."""
    if size < 1:
        raise ValueError("size must be >= 1")
    buf: List[str] = []
    for line in lines:
        buf.append(line)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


def chunk_by_seconds(lines: Iterable[str], seconds: float) -> Iterator[List[str]]:
    """Yield chunks where each chunk spans at most *seconds* of log time.

    Lines without a parseable timestamp are appended to the current chunk.
    """
    if seconds <= 0:
        raise ValueError("seconds must be > 0")
    buf: List[str] = []
    window_start: Optional[float] = None

    for line in lines:
        ts = extract_timestamp(line)
        if ts is not None:
            epoch = ts.timestamp()
            if window_start is None:
                window_start = epoch
            elif epoch - window_start >= seconds:
                if buf:
                    yield buf
                buf = []
                window_start = epoch
        buf.append(line)

    if buf:
        yield buf


def chunk_file(path: str, *, size: Optional[int] = None,
               seconds: Optional[float] = None) -> Iterator[List[str]]:
    """Open *path* and yield chunks according to *size* or *seconds*."""
    if size is None and seconds is None:
        raise ValueError("Provide either size or seconds")
    with open(path, "r", errors="replace") as fh:
        lines = list(fh)
    if size is not None:
        yield from chunk_by_count(lines, size)
    else:
        yield from chunk_by_seconds(lines, seconds)  # type: ignore[arg-type]
