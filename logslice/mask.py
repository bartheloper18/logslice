"""Line masking: hide or replace specific fields/columns in log output."""

from __future__ import annotations

import re
from typing import Iterable, Iterator, Optional

_PLACEHOLDER = "***"


def mask_positions(line: str, start: int, end: int, placeholder: str = _PLACEHOLDER) -> str:
    """Replace characters from *start* to *end* (exclusive) with *placeholder*."""
    if start < 0 or end > len(line) or start >= end:
        return line
    return line[:start] + placeholder + line[end:]


def mask_pattern(
    line: str,
    pattern: re.Pattern,
    placeholder: str = _PLACEHOLDER,
    group: int = 0,
) -> str:
    """Replace every match of *pattern* (or a specific capture group) with *placeholder*."""

    def _replace(m: re.Match) -> str:  # type: ignore[type-arg]
        try:
            span = m.span(group)
        except IndexError:
            span = m.span(0)
        full = m.group(0)
        rel_start = span[0] - m.start(0)
        rel_end = span[1] - m.start(0)
        return full[:rel_start] + placeholder + full[rel_end:]

    return pattern.sub(_replace, line)


def mask_field(
    line: str,
    field_name: str,
    placeholder: str = _PLACEHOLDER,
    sep: str = "=",
) -> str:
    """Mask the value of a key=value field in *line*."""
    pat = re.compile(
        r"(?<="
        + re.escape(field_name)
        + re.escape(sep)
        + r")[^\s,;|]+"
    )
    return pat.sub(placeholder, line)


def mask_lines(
    lines: Iterable[str],
    pattern: Optional[re.Pattern] = None,  # type: ignore[type-arg]
    field: Optional[str] = None,
    placeholder: str = _PLACEHOLDER,
) -> Iterator[str]:
    """Apply masking to each line in *lines*."""
    for line in lines:
        stripped = line.rstrip("\n")
        if pattern is not None:
            stripped = mask_pattern(stripped, pattern, placeholder)
        if field is not None:
            stripped = mask_field(stripped, field, placeholder)
        yield stripped + ("\n" if line.endswith("\n") else "")
