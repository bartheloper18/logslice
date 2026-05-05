"""Grep-style pattern matching for log lines."""

import re
from typing import Iterable, Iterator, Optional, Pattern


def compile_pattern(
    pattern: str,
    ignore_case: bool = False,
    fixed_string: bool = False,
) -> Pattern[str]:
    """Compile a search pattern into a regex.

    Args:
        pattern: The search string or regex pattern.
        ignore_case: Whether to ignore case when matching.
        fixed_string: Treat pattern as a literal string (no regex).

    Returns:
        A compiled regular expression object.
    """
    if fixed_string:
        pattern = re.escape(pattern)
    flags = re.IGNORECASE if ignore_case else 0
    return re.compile(pattern, flags)


def grep_lines(
    lines: Iterable[str],
    pattern: Pattern[str],
    invert: bool = False,
) -> Iterator[str]:
    """Yield lines that match (or don't match) the given pattern.

    Args:
        lines: Iterable of log lines to search.
        pattern: Compiled regex pattern.
        invert: If True, yield lines that do NOT match.

    Yields:
        Matching (or non-matching) lines.
    """
    for line in lines:
        matched = pattern.search(line) is not None
        if matched ^ invert:
            yield line


def grep_file(
    filepath: str,
    pattern: Pattern[str],
    invert: bool = False,
    encoding: str = "utf-8",
) -> Iterator[str]:
    """Yield matching lines from a file.

    Args:
        filepath: Path to the log file.
        pattern: Compiled regex pattern.
        invert: If True, yield lines that do NOT match.
        encoding: File encoding.

    Yields:
        Matching lines from the file.
    """
    with open(filepath, "r", encoding=encoding, errors="replace") as fh:
        yield from grep_lines(fh, pattern, invert=invert)


def count_matches(
    lines: Iterable[str],
    pattern: Pattern[str],
    invert: bool = False,
) -> int:
    """Count how many lines match the pattern."""
    return sum(1 for _ in grep_lines(lines, pattern, invert=invert))
