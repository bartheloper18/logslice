"""Filter log lines by severity level."""

from __future__ import annotations

import re
from typing import Iterable, Iterator, List, Optional

# Ordered from lowest to highest severity
LEVEL_ORDER: List[str] = ["debug", "info", "notice", "warning", "warn", "error", "critical", "fatal"]

# Canonical mapping: aliases -> canonical name
_CANONICAL: dict[str, str] = {
    "debug": "debug",
    "info": "info",
    "notice": "notice",
    "warning": "warning",
    "warn": "warning",
    "error": "error",
    "err": "error",
    "critical": "critical",
    "crit": "critical",
    "fatal": "fatal",
}

_SEVERITY: dict[str, int] = {
    "debug": 0,
    "info": 1,
    "notice": 2,
    "warning": 3,
    "error": 4,
    "critical": 5,
    "fatal": 6,
}

_LEVEL_RE = re.compile(
    r"\b(debug|info|notice|warn(?:ing)?|err(?:or)?|crit(?:ical)?|fatal)\b",
    re.IGNORECASE,
)


def canonicalize(level: str) -> Optional[str]:
    """Return the canonical level name, or None if unrecognised."""
    return _CANONICAL.get(level.lower())


def severity(level: str) -> int:
    """Return numeric severity for a canonical level name (unknown -> -1)."""
    return _SEVERITY.get(_CANONICAL.get(level.lower(), ""), -1)


def extract_level(line: str) -> Optional[str]:
    """Return the first recognised level token found in *line*, canonical form."""
    m = _LEVEL_RE.search(line)
    if m:
        return canonicalize(m.group(1))
    return None


def filter_by_level(
    lines: Iterable[str],
    min_level: str,
    max_level: Optional[str] = None,
) -> Iterator[str]:
    """Yield lines whose level is between *min_level* and *max_level* (inclusive).

    Lines with no detectable level are dropped.
    """
    min_sev = severity(min_level)
    max_sev = severity(max_level) if max_level else 999
    for line in lines:
        lvl = extract_level(line)
        if lvl is None:
            continue
        sev = severity(lvl)
        if min_sev <= sev <= max_sev:
            yield line


def filter_level_file(
    path: str,
    min_level: str,
    max_level: Optional[str] = None,
    encoding: str = "utf-8",
) -> Iterator[str]:
    """Open *path* and yield lines matching the level range."""
    with open(path, encoding=encoding, errors="replace") as fh:
        yield from filter_by_level(fh, min_level, max_level)
