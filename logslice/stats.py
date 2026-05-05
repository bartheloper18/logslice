"""Log statistics collection and reporting."""

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

LEVEL_PATTERN = re.compile(
    r'\b(DEBUG|INFO|NOTICE|WARNING|WARN|ERROR|CRITICAL|FATAL)\b',
    re.IGNORECASE
)


@dataclass
class LogStats:
    """Aggregated statistics for a set of log lines."""
    total_lines: int = 0
    matched_lines: int = 0
    level_counts: Dict[str, int] = field(default_factory=Counter)
    first_timestamp: Optional[str] = None
    last_timestamp: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "total_lines": self.total_lines,
            "matched_lines": self.matched_lines,
            "level_counts": dict(self.level_counts),
            "first_timestamp": self.first_timestamp,
            "last_timestamp": self.last_timestamp,
        }


def extract_level(line: str) -> Optional[str]:
    """Extract the log level from a line, or None if not found."""
    m = LEVEL_PATTERN.search(line)
    if m:
        return m.group(1).upper()
    return None


def collect_stats(all_lines: List[str], matched_lines: List[str],
                  extract_ts=None) -> LogStats:
    """Build a LogStats object from raw and filtered line lists.

    Args:
        all_lines: Every line in the source (used for total count).
        matched_lines: Lines that survived time-range filtering.
        extract_ts: Optional callable(line) -> datetime | None for timestamps.
    """
    stats = LogStats(
        total_lines=len(all_lines),
        matched_lines=len(matched_lines),
    )

    counts: Counter = Counter()
    for line in matched_lines:
        level = extract_level(line)
        if level:
            counts[level] += 1
        if extract_ts is not None:
            ts = extract_ts(line)
            if ts is not None:
                ts_str = str(ts)
                if stats.first_timestamp is None:
                    stats.first_timestamp = ts_str
                stats.last_timestamp = ts_str

    stats.level_counts = counts
    return stats


def format_stats(stats: LogStats) -> str:
    """Render a LogStats object as a human-readable summary string."""
    lines = [
        f"Total lines   : {stats.total_lines}",
        f"Matched lines : {stats.matched_lines}",
    ]
    if stats.first_timestamp:
        lines.append(f"First ts      : {stats.first_timestamp}")
    if stats.last_timestamp:
        lines.append(f"Last ts       : {stats.last_timestamp}")
    if stats.level_counts:
        lines.append("Level counts  :")
        for lvl, cnt in sorted(stats.level_counts.items()):
            lines.append(f"  {lvl:<10}: {cnt}")
    return "\n".join(lines)
