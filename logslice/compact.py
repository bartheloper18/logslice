"""Compact multi-line JSON log entries into single lines."""

from __future__ import annotations

import json
from typing import Iterable, Iterator, TextIO


def _try_flush(buf: list[str]) -> str | None:
    """Attempt to parse accumulated buffer as JSON; return compact form or None."""
    raw = "".join(buf).strip()
    if not raw:
        return None
    try:
        obj = json.loads(raw)
        return json.dumps(obj, separators=(",", ":"))
    except json.JSONDecodeError:
        return None


def compact_lines(lines: Iterable[str]) -> Iterator[str]:
    """Yield compacted lines.

    Multi-line JSON objects/arrays are collapsed to a single line.
    Lines that are already single-line JSON are re-serialised without
    extra whitespace.  Non-JSON lines are passed through unchanged.
    """
    buf: list[str] = []
    depth = 0

    for line in lines:
        stripped = line.rstrip("\n")

        if not buf:
            # Check whether this line starts a multi-line JSON block.
            candidate = stripped.lstrip()
            if candidate.startswith("{") or candidate.startswith("["):
                depth = candidate.count("{") + candidate.count("[") - candidate.count("}") - candidate.count("]")
                buf.append(stripped)
                if depth <= 0:
                    # Entire JSON object fits on one line.
                    result = _try_flush(buf)
                    buf.clear()
                    yield (result if result is not None else stripped) + "\n"
            else:
                yield line if line.endswith("\n") else line + "\n"
        else:
            depth += stripped.count("{") + stripped.count("[") - stripped.count("}") - stripped.count("]")
            buf.append(stripped)
            if depth <= 0:
                result = _try_flush(buf)
                buf.clear()
                depth = 0
                if result is not None:
                    yield result + "\n"
                else:
                    # Could not parse; emit buffered lines as-is.
                    for buffered in buf:
                        yield buffered + "\n"
                    buf.clear()

    # Flush any remaining buffer.
    if buf:
        result = _try_flush(buf)
        if result is not None:
            yield result + "\n"
        else:
            for buffered in buf:
                yield buffered + "\n"


def compact_file(in_file: TextIO, out_file: TextIO) -> int:
    """Compact *in_file* writing results to *out_file*.

    Returns the number of lines written.
    """
    count = 0
    for line in compact_lines(in_file):
        out_file.write(line)
        count += 1
    return count
