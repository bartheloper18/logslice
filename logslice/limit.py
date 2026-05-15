"""Byte-limit filtering: drop or truncate output once a byte budget is reached."""

from __future__ import annotations

from typing import Iterable, Iterator, IO


def limit_lines(
    lines: Iterable[str],
    max_bytes: int,
    *,
    truncate: bool = False,
) -> Iterator[str]:
    """Yield lines until *max_bytes* of output have been produced.

    Parameters
    ----------
    lines:
        Source lines (may or may not end with ``\\n``).
    max_bytes:
        Hard budget in bytes.  Once reached (or exceeded) no further lines
        are emitted unless *truncate* is True.
    truncate:
        When True the line that would exceed the budget is itself truncated
        so that the total output is exactly *max_bytes* bytes rather than
        being dropped entirely.
    """
    if max_bytes <= 0:
        return

    remaining = max_bytes
    for line in lines:
        encoded = line.encode()
        size = len(encoded)
        if size <= remaining:
            remaining -= size
            yield line
            if remaining == 0:
                return
        else:
            if truncate and remaining > 0:
                yield encoded[:remaining].decode(errors="replace")
            return


def limit_file(
    path: str,
    max_bytes: int,
    out: IO[str],
    *,
    truncate: bool = False,
) -> int:
    """Read *path* and write byte-limited output to *out*.

    Returns the number of lines written.
    """
    written = 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in limit_lines(fh, max_bytes, truncate=truncate):
            out.write(line)
            written += 1
    return written
