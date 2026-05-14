"""squash.py – collapse repeated/similar log lines into a single summary.

Two lines are considered "similar" when they differ only in numeric tokens
(timestamps, IDs, counts, etc.).  Adjacent similar lines are merged into one
representative line with a repetition count appended.
"""
from __future__ import annotations

import re
from typing import Iterable, Iterator

_NUMBERS = re.compile(r"\b\d+\b")


def _signature(line: str) -> str:
    """Return a normalised signature with all decimal numbers replaced by '#'."""
    return _NUMBERS.sub("#", line.rstrip("\n"))


def squash_lines(
    lines: Iterable[str],
    *,
    min_repeat: int = 2,
) -> Iterator[str]:
    """Yield lines with consecutive similar lines collapsed.

    Parameters
    ----------
    lines:
        Input lines (may include newlines).
    min_repeat:
        Minimum number of occurrences before collapsing; groups smaller than
        this are emitted verbatim.
    """
    buf: list[str] = []
    cur_sig: str | None = None

    def _flush() -> Iterator[str]:
        if not buf:
            return
        if len(buf) >= min_repeat:
            rep = buf[0].rstrip("\n")
            yield f"{rep}  [repeated {len(buf)}x]\n"
        else:
            yield from buf
        buf.clear()

    for line in lines:
        sig = _signature(line)
        if sig == cur_sig:
            buf.append(line)
        else:
            yield from _flush()
            cur_sig = sig
            buf.append(line)

    yield from _flush()


def squash_file(
    path: str,
    *,
    min_repeat: int = 2,
    encoding: str = "utf-8",
) -> Iterator[str]:
    """Open *path* and yield squashed lines."""
    with open(path, encoding=encoding) as fh:
        yield from squash_lines(fh, min_repeat=min_repeat)
