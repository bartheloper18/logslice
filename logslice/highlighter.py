"""ANSI color helpers for log-level tokens and timestamps."""

from __future__ import annotations

import re
import sys
from typing import IO

# ---------------------------------------------------------------------------
# ANSI codes
# ---------------------------------------------------------------------------
_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"

_LEVEL_COLORS = {
    "error": _RED + _BOLD,
    "err": _RED + _BOLD,
    "critical": _RED + _BOLD,
    "fatal": _RED + _BOLD,
    "warning": _YELLOW,
    "warn": _YELLOW,
    "info": _GREEN,
    "debug": _CYAN,
}

# Matches common log-level tokens (case-insensitive, whole word)
_LEVEL_RE = re.compile(
    r"\b(CRITICAL|FATAL|ERROR|ERR|WARNING|WARN|INFO|DEBUG)\b"
)

# Matches ISO-8601-ish timestamps and Apache/syslog-style dates
_TS_RE = re.compile(
    r"(?:"
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?"  # ISO
    r"|\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4}"  # Apache
    r"|[A-Za-z]{3} [ \d]\d \d{2}:\d{2}:\d{2}"  # syslog
    r")"
)


def supports_color(stream: IO = sys.stdout) -> bool:  # type: ignore[assignment]
    """Return True when *stream* looks like a colour-capable terminal."""
    return hasattr(stream, "isatty") and stream.isatty()


def highlight_level(token: str) -> str:
    """Wrap *token* in the appropriate ANSI colour for its log level."""
    color = _LEVEL_COLORS.get(token.lower(), "")
    if color:
        return f"{color}{token}{_RESET}"
    return token


def replace_level(match: re.Match) -> str:  # type: ignore[type-arg]
    return highlight_level(match.group(0))


def highlight_timestamp(text: str) -> str:
    """Wrap timestamp substrings in *text* with a dim/cyan colour."""
    return _TS_RE.sub(lambda m: f"{_CYAN}{m.group(0)}{_RESET}", text)


def highlight_line(line: str, *, color: bool = True, timestamps: bool = True) -> str:
    """Return *line* with ANSI highlights applied.

    When *color* is False the original line is returned unchanged.
    When *timestamps* is False only log-level tokens are highlighted.
    """
    if not color:
        return line
    result = _LEVEL_RE.sub(replace_level, line)
    if timestamps:
        result = highlight_timestamp(result)
    return result
