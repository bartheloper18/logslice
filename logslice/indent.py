"""Indent / outdent log lines by a fixed number of spaces or a prefix string."""

from __future__ import annotations

import re
from typing import Iterable, Iterator


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_newline(line: str) -> tuple[str, str]:
    """Return (body, terminator) splitting off a trailing newline if present."""
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def indent_line(line: str, prefix: str) -> str:
    """Prepend *prefix* to *line*, preserving any trailing newline."""
    body, nl = _strip_newline(line)
    return f"{prefix}{body}{nl}"


def outdent_line(line: str, prefix: str) -> str:
    """Remove a leading *prefix* from *line* if present, else return unchanged."""
    body, nl = _strip_newline(line)
    if body.startswith(prefix):
        return f"{body[len(prefix):]}{nl}"
    return line


def indent_lines(
    lines: Iterable[str],
    prefix: str = "    ",
    *,
    outdent: bool = False,
) -> Iterator[str]:
    """Yield each line with *prefix* added (or removed when *outdent* is True)."""
    fn = outdent_line if outdent else indent_line
    for line in lines:
        yield fn(line, prefix)


def indent_file(
    path: str,
    prefix: str = "    ",
    *,
    outdent: bool = False,
    out=None,
) -> None:
    """Read *path* and write indented/outdented lines to *out* (default: stdout)."""
    import sys

    sink = out if out is not None else sys.stdout
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in indent_lines(fh, prefix, outdent=outdent):
            sink.write(line)
