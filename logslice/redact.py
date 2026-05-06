"""Redaction of sensitive patterns from log lines."""

import re
from typing import Iterable, Iterator, List, Optional, Tuple

# Built-in named patterns
BUILTIN_PATTERNS: dict = {
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "email": r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b",
    "token": r"\b(?:Bearer\s+)?[A-Za-z0-9_\-]{20,}\b",
    "credit_card": r"\b(?:\d[ -]?){13,16}\b",
    "uuid": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
}

DEFAULT_MASK = "[REDACTED]"


def compile_redact_patterns(
    patterns: List[str],
    builtins: Optional[List[str]] = None,
    ignore_case: bool = False,
) -> List[re.Pattern]:
    """Compile a list of regex patterns (and optional builtins) for redaction."""
    flags = re.IGNORECASE if ignore_case else 0
    compiled: List[re.Pattern] = []
    for name in builtins or []:
        raw = BUILTIN_PATTERNS.get(name)
        if raw is None:
            raise ValueError(f"Unknown built-in redact pattern: {name!r}")
        compiled.append(re.compile(raw, flags))
    for raw in patterns:
        compiled.append(re.compile(raw, flags))
    return compiled


def redact_line(
    line: str,
    patterns: List[re.Pattern],
    mask: str = DEFAULT_MASK,
) -> Tuple[str, int]:
    """Replace all matches in *line* with *mask*.

    Returns (redacted_line, number_of_replacements).
    """
    count = 0
    for pat in patterns:
        new_line, n = pat.subn(mask, line)
        line = new_line
        count += n
    return line, count


def redact_lines(
    lines: Iterable[str],
    patterns: List[re.Pattern],
    mask: str = DEFAULT_MASK,
) -> Iterator[str]:
    """Yield redacted versions of each line."""
    for line in lines:
        redacted, _ = redact_line(line, patterns, mask)
        yield redacted


def redact_file(
    path: str,
    patterns: List[re.Pattern],
    mask: str = DEFAULT_MASK,
) -> Iterator[str]:
    """Open *path* and yield redacted lines."""
    with open(path, "r", errors="replace") as fh:
        yield from redact_lines(fh, patterns, mask)
