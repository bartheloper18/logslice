"""clip.py – extract a line-number range from a stream or file."""
from __future__ import annotations

from typing import Iterable, Iterator, Optional, TextIO


def clip_lines(
    lines: Iterable[str],
    start: int,
    end: Optional[int] = None,
) -> Iterator[str]:
    """Yield lines whose 1-based index falls within [start, end].

    Args:
        lines:  Iterable of raw log lines.
        start:  First line to include (1-based, inclusive).
        end:    Last line to include (1-based, inclusive).  ``None`` means
                read until EOF.

    Yields:
        Lines that fall within the requested range, preserving content.
    """
    if start < 1:
        raise ValueError(f"start must be >= 1, got {start}")
    if end is not None and end < start:
        raise ValueError(f"end ({end}) must be >= start ({start})")

    for lineno, line in enumerate(lines, 1):
        if lineno < start:
            continue
        if end is not None and lineno > end:
            break
        yield line


def clip_file(
    path: str,
    start: int,
    end: Optional[int] = None,
    out: Optional[TextIO] = None,
) -> int:
    """Clip *path* and write matching lines to *out*.

    Returns the number of lines written.
    """
    import sys

    sink = out or sys.stdout
    count = 0
    with open(path, "r", errors="replace") as fh:
        for line in clip_lines(fh, start=start, end=end):
            sink.write(line)
            count += 1
    return count
