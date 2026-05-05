"""Terminal color highlighting for matched log lines and timestamps."""

import re
from typing import Optional

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_CYAN = "\033[36m"
ANSI_MAGENTA = "\033[35m"

LEVEL_COLORS = {
    "ERROR": ANSI_RED,
    "WARN": ANSI_YELLOW,
    "WARNING": ANSI_YELLOW,
    "INFO": ANSI_GREEN,
    "DEBUG": ANSI_CYAN,
    "CRITICAL": ANSI_MAGENTA,
    "FATAL": ANSI_MAGENTA,
}

LEVEL_PATTERN = re.compile(
    r"\b(ERROR|WARN(?:ING)?|INFO|DEBUG|CRITICAL|FATAL)\b"
)


def supports_color() -> bool:
    """Return True if the terminal likely supports ANSI color codes."""
    import sys
    import os
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and os.name != "nt"


def highlight_level(line: str) -> str:
    """Colorize log level keywords within a line."""
    def replace_level(match: re.Match) -> str:
        level = match.group(1)
        color = LEVEL_COLORS.get(level, ANSI_RESET)
        return f"{color}{ANSI_BOLD}{level}{ANSI_RESET}"

    return LEVEL_PATTERN.sub(replace_level, line)


def highlight_timestamp(line: str, timestamp_str: Optional[str]) -> str:
    """Highlight the timestamp portion of a line in cyan."""
    if not timestamp_str:
        return line
    escaped = re.escape(timestamp_str)
    return re.sub(
        escaped,
        f"{ANSI_CYAN}{timestamp_str}{ANSI_RESET}",
        line,
        count=1,
    )


def highlight_line(line: str, timestamp_str: Optional[str] = None, use_color: bool = True) -> str:
    """Apply all highlighting to a log line."""
    if not use_color:
        return line
    line = highlight_timestamp(line, timestamp_str)
    line = highlight_level(line)
    return line
