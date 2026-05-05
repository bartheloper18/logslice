"""CLI helpers for the --tail / --follow flag in logslice."""

import sys
from typing import Optional

from logslice.tail import read_last_lines, follow_file
from logslice.output import format_line
from logslice.highlighter import highlight_line


def run_tail(
    path: str,
    lines: int = 10,
    follow: bool = False,
    color: bool = False,
    out=None,
) -> None:
    """Print the last *lines* of *path*, then optionally follow new output.

    Parameters
    ----------
    path:   Log file to read.
    lines:  Number of historical lines to show before following.
    follow: If True, keep watching for new lines (like ``tail -f``).
    color:  Apply ANSI colour highlighting to each line.
    out:    Output stream (defaults to sys.stdout).
    """
    if out is None:
        out = sys.stdout

    def _emit(line: str, lineno: Optional[int] = None) -> None:
        text = line.rstrip("\n")
        if color:
            text = highlight_line(text)
        formatted = format_line(text, line_number=lineno, color=color)
        out.write(formatted + "\n")
        out.flush()

    # Print historical tail
    historical = read_last_lines(path, lines)
    for raw in historical:
        _emit(raw)

    if not follow:
        return

    # Follow mode
    try:
        follow_file(path, callback=_emit)
    except KeyboardInterrupt:
        pass
