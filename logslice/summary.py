"""High-level summary entry point used by the CLI."""

import sys
from typing import List, Optional, TextIO

from logslice.stats import collect_stats, format_stats
from logslice.parser import extract_timestamp


def summarise_lines(
    all_lines: List[str],
    matched_lines: List[str],
    out: Optional[TextIO] = None,
    use_color: bool = False,
) -> str:
    """Collect stats and return (and optionally print) a summary.

    Args:
        all_lines: Every line read from the source file.
        matched_lines: Lines that passed time-range filtering.
        out: If provided, the summary is written here.
        use_color: Reserved for future ANSI colouring of the summary.

    Returns:
        The formatted summary string.
    """
    stats = collect_stats(
        all_lines,
        matched_lines,
        extract_ts=extract_timestamp,
    )
    summary = format_stats(stats)

    if out is not None:
        out.write(summary + "\n")

    return summary


def summarise_file(
    path: str,
    matched_lines: List[str],
    out: Optional[TextIO] = None,
    use_color: bool = False,
) -> str:
    """Read *path*, collect stats against *matched_lines*, and print summary.

    Args:
        path: Path to the original log file (used to get total line count).
        matched_lines: Lines that passed time-range filtering.
        out: If provided, the summary is written here.
        use_color: Reserved for future ANSI colouring of the summary.

    Returns:
        The formatted summary string.
    """
    try:
        with open(path, "r", errors="replace") as fh:
            all_lines = fh.readlines()
    except OSError as exc:
        msg = f"logslice: cannot open '{path}': {exc}\n"
        (out or sys.stderr).write(msg)
        return ""

    return summarise_lines(all_lines, matched_lines, out=out, use_color=use_color)
