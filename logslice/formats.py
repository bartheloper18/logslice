"""Predefined log format definitions for common logging systems."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogFormat:
    """Describes a known log format with its timestamp pattern and position."""
    name: str
    pattern: re.Pattern
    timestamp_group: str = "timestamp"
    description: str = ""


# Common log format definitions
FORMATS = {
    "iso8601": LogFormat(
        name="iso8601",
        pattern=re.compile(
            r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)"
        ),
        description="ISO 8601 datetime (e.g. 2024-01-15T12:00:00Z)",
    ),
    "apache": LogFormat(
        name="apache",
        pattern=re.compile(
            r"\[(?P<timestamp>\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\]"
        ),
        description="Apache/Nginx combined log format",
    ),
    "syslog": LogFormat(
        name="syslog",
        pattern=re.compile(
            r"(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
        ),
        description="Syslog format (e.g. Jan 15 12:00:00)",
    ),
    "epoch": LogFormat(
        name="epoch",
        pattern=re.compile(
            r"(?P<timestamp>\d{10}(?:\.\d+)?)"
        ),
        description="Unix epoch timestamp (seconds)",
    ),
    "epoch_ms": LogFormat(
        name="epoch_ms",
        pattern=re.compile(
            r"(?P<timestamp>\d{13})"
        ),
        description="Unix epoch timestamp (milliseconds)",
    ),
}


def detect_format(line: str) -> Optional[LogFormat]:
    """Attempt to detect the log format of a given line."""
    for fmt in FORMATS.values():
        if fmt.pattern.search(line):
            return fmt
    return None


def list_formats() -> list:
    """Return a list of (name, description) tuples for all known formats."""
    return [(name, fmt.description) for name, fmt in FORMATS.items()]
