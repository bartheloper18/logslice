"""Line truncation utilities for long log lines."""

from typing import Iterable, Iterator, Optional

DEFAULT_MAX_WIDTH = 200
_ELLIPSIS = "..."


def truncate_line(line: str, max_width: int = DEFAULT_MAX_WIDTH, ellipsis: str = _ELLIPSIS) -> str:
    """Return *line* truncated to *max_width* characters.

    If the line (after stripping the trailing newline) exceeds *max_width*,
    the returned string ends with *ellipsis* so that the total length equals
    *max_width*.  A trailing newline is preserved when present.
    """
    if max_width <= 0:
        raise ValueError("max_width must be a positive integer")

    has_newline = line.endswith("\n")
    content = line.rstrip("\n")

    if len(content) <= max_width:
        return line  # nothing to do

    cut = max_width - len(ellipsis)
    if cut < 0:
        cut = 0
    truncated = content[:cut] + ellipsis
    return truncated + ("\n" if has_newline else "")


def truncate_lines(
    lines: Iterable[str],
    max_width: int = DEFAULT_MAX_WIDTH,
    ellipsis: str = _ELLIPSIS,
) -> Iterator[str]:
    """Yield each line from *lines* truncated to *max_width* characters."""
    for line in lines:
        yield truncate_line(line, max_width=max_width, ellipsis=ellipsis)


def truncate_file(
    path: str,
    max_width: int = DEFAULT_MAX_WIDTH,
    ellipsis: str = _ELLIPSIS,
    encoding: str = "utf-8",
    out=None,
) -> None:
    """Read *path* and write truncated lines to *out* (default: stdout)."""
    import sys

    sink = out if out is not None else sys.stdout
    with open(path, "r", encoding=encoding) as fh:
        for line in truncate_lines(fh, max_width=max_width, ellipsis=ellipsis):
            sink.write(line)
