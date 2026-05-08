"""Compute log event rates over time windows."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from logslice.parser import extract_timestamp


def _floor_to_window(dt: datetime, window_seconds: int) -> datetime:
    """Floor a datetime to the nearest window boundary."""
    epoch = datetime(1970, 1, 1, tzinfo=dt.tzinfo)
    delta = int((dt - epoch).total_seconds())
    floored = delta - (delta % window_seconds)
    return epoch + timedelta(seconds=floored)


def bucket_lines(
    lines: Iterable[str],
    window_seconds: int = 60,
) -> Dict[datetime, int]:
    """Count log lines per time bucket.

    Lines without a parseable timestamp are ignored.

    Args:
        lines: Iterable of raw log lines.
        window_seconds: Bucket width in seconds (default 60).

    Returns:
        Ordered dict mapping bucket start time -> event count.
    """
    counts: Dict[datetime, int] = defaultdict(int)
    for line in lines:
        ts = extract_timestamp(line)
        if ts is None:
            continue
        bucket = _floor_to_window(ts, window_seconds)
        counts[bucket] += 1
    return dict(sorted(counts.items()))


def iter_rate(
    lines: Iterable[str],
    window_seconds: int = 60,
) -> Iterator[Tuple[datetime, int]]:
    """Yield (bucket_start, count) pairs in chronological order."""
    for bucket, count in bucket_lines(lines, window_seconds).items():
        yield bucket, count


def format_rate(
    buckets: Dict[datetime, int],
    window_seconds: int = 60,
    label: str = "events",
) -> List[str]:
    """Format bucketed counts as human-readable lines.

    Args:
        buckets: Mapping returned by :func:`bucket_lines`.
        window_seconds: Bucket width used when building *buckets*.
        label: Noun to use in the output (e.g. ``'events'``).

    Returns:
        List of formatted strings, one per bucket.
    """
    lines: List[str] = []
    for bucket, count in sorted(buckets.items()):
        ts_str = bucket.strftime("%Y-%m-%d %H:%M:%S")
        rate = count / window_seconds
        lines.append(
            f"{ts_str}  {count:>6} {label}  ({rate:.2f}/s)"
        )
    return lines
