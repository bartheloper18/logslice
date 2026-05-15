"""head.py – emit the first N lines of a log file or stream."""

from __future__ import annotations

import io
from typing import Iterable, Iterator, TextIO


def head_lines(lines: Iterable[str], n: int = 10) -> Iterator[str]:
    """Yield at most *n* lines from *lines*.

    Parameters
    ----------
    lines:
        Any iterable of strings (with or without trailing newlines).
    n:
        Maximum number of lines to yield.  If *n* is 0 or negative the
        generator yields nothing.
    """
    if n <= 0:
        return
    count = 0
    for line in lines:
        yield line
        count += 1
        if count >= n:
            return


def head_file(
    path: str,
    n: int = 10,
    out: TextIO | None = None,
) -> int:
    """Print the first *n* lines of the file at *path* to *out*.

    Parameters
    ----------
    path:
        Path to the log file to read.
    n:
        Number of lines to emit (default 10).
    out:
        Output stream; defaults to *sys.stdout*.

    Returns
    -------
    int
        The number of lines actually written.
    """
    import sys

    if out is None:
        out = sys.stdout

    written = 0
    with open(path, "r", errors="replace") as fh:
        for line in head_lines(fh, n=n):
            out.write(line if line.endswith("\n") else line + "\n")
            written += 1
    return written
