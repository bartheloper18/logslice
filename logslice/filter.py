"""Time-range filter: yields log lines whose timestamps fall within [start, end]."""

from datetime import datetime
from typing import IO, Iterator, Optional

from logslice.parser import extract_timestamp


def filter_lines(
    stream: IO[str],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    include_unparseable: bool = False,
) -> Iterator[str]:
    """
    Yield lines from *stream* that fall within the [start, end] time range.

    Parameters
    ----------
    stream:              Any file-like object yielding text lines.
    start:               Inclusive lower bound (None = no lower bound).
    end:                 Inclusive upper bound (None = no upper bound).
    include_unparseable: If True, lines with no detectable timestamp are
                         always included; otherwise they are dropped.
    """
    for line in stream:
        stripped = line.rstrip('\n')
        if not stripped:
            continue

        ts = extract_timestamp(stripped)

        if ts is None:
            if include_unparseable:
                yield stripped
            continue

        if start is not None and ts < start:
            continue
        if end is not None and ts > end:
            continue

        yield stripped


def filter_file(
    path: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    include_unparseable: bool = False,
) -> Iterator[str]:
    """Convenience wrapper that opens *path* and delegates to filter_lines."""
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        yield from filter_lines(fh, start=start, end=end,
                                 include_unparseable=include_unparseable)
