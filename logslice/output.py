"""Output formatting and writing for filtered log results."""

import sys
from typing import Iterable, Optional, TextIO

from logslice.highlighter import highlight_line, supports_color
from logslice.parser import extract_timestamp


def format_line(
    line: str,
    use_color: bool = False,
    show_line_numbers: bool = False,
    line_number: Optional[int] = None,
) -> str:
    """Format a single output line with optional color and line numbers."""
    ts_match = extract_timestamp(line)
    timestamp_str = ts_match.group(0) if ts_match else None

    if show_line_numbers and line_number is not None:
        prefix = f"{line_number:>6}: "
    else:
        prefix = ""

    formatted = highlight_line(line.rstrip("\n"), timestamp_str, use_color=use_color)
    return f"{prefix}{formatted}"


def write_output(
    lines: Iterable[str],
    output: TextIO = sys.stdout,
    use_color: Optional[bool] = None,
    show_line_numbers: bool = False,
    count_only: bool = False,
) -> int:
    """
    Write filtered log lines to the given output stream.

    Returns the number of lines written.
    """
    if use_color is None:
        use_color = supports_color()

    count = 0
    for i, line in enumerate(lines, start=1):
        count += 1
        if not count_only:
            formatted = format_line(
                line,
                use_color=use_color,
                show_line_numbers=show_line_numbers,
                line_number=i,
            )
            output.write(formatted + "\n")

    if count_only:
        output.write(f"{count}\n")

    return count
