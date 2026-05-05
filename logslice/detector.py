"""Auto-detection of log format from a sample of lines."""

from collections import Counter
from typing import Optional

from logslice.formats import LogFormat, detect_format


DEFAULT_SAMPLE_SIZE = 20


def detect_format_from_lines(lines: list, sample_size: int = DEFAULT_SAMPLE_SIZE) -> Optional[LogFormat]:
    """
    Detect the predominant log format from a list of lines.

    Samples up to `sample_size` non-empty lines and returns the most
    frequently detected format, or None if no format is detected.
    """
    sample = [line for line in lines if line.strip()][:sample_size]
    if not sample:
        return None

    counts: Counter = Counter()
    detected: dict = {}

    for line in sample:
        fmt = detect_format(line)
        if fmt:
            counts[fmt.name] += 1
            detected[fmt.name] = fmt

    if not counts:
        return None

    best_name, _ = counts.most_common(1)[0]
    return detected[best_name]


def detect_format_from_file(filepath: str, sample_size: int = DEFAULT_SAMPLE_SIZE) -> Optional[LogFormat]:
    """
    Detect the log format by reading the first `sample_size` lines of a file.
    """
    try:
        with open(filepath, "r", errors="replace") as fh:
            lines = [fh.readline() for _ in range(sample_size)]
    except OSError as exc:
        raise OSError(f"Cannot read file for format detection: {filepath}") from exc

    return detect_format_from_lines(lines, sample_size=sample_size)
