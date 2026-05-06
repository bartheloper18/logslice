"""CLI sub-command: logslice rotate — stream lines across rotated log files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from logslice.rotate import find_rotated_files, iter_rotated_lines
from logslice.filter import filter_lines
from logslice.output import format_line, write_output


def run_rotate(
    logfile: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    no_gz: bool = False,
    number: bool = False,
    color: bool = False,
    out=None,
) -> None:
    """Stream lines from *logfile* and its rotated siblings.

    Parameters
    ----------
    logfile:  Path to the active (current) log file.
    start:    ISO-8601 timestamp lower bound (inclusive).
    end:      ISO-8601 timestamp upper bound (inclusive).
    no_gz:    Skip compressed rotated files.
    number:   Prefix each output line with its sequence number.
    color:    Highlight log-level keywords with ANSI colours.
    out:      File-like object to write to (defaults to *sys.stdout*).
    """
    if out is None:
        out = sys.stdout

    base = Path(logfile)
    if not base.exists():
        print(f"logslice rotate: file not found: {logfile}", file=sys.stderr)
        sys.exit(1)

    rotated = find_rotated_files(base, include_gz=not no_gz)
    n_files = len(rotated)

    # Inform the user which files will be scanned
    print(
        f"# Scanning {n_files} file(s): {', '.join(p.name for p in rotated)}",
        file=out,
    )

    raw_lines: List[str] = list(iter_rotated_lines(base, include_gz=not no_gz))

    if start or end:
        filtered = list(filter_lines(raw_lines, start=start, end=end))
    else:
        filtered = raw_lines

    write_output(filtered, out=out, number=number, color=color)


def build_rotate_parser(subparsers) -> None:  # type: ignore[type-arg]
    """Attach the *rotate* sub-command to an existing subparsers action."""
    p: argparse.ArgumentParser = subparsers.add_parser(
        'rotate',
        help='Stream lines across the active log file and its rotated siblings.',
    )
    p.add_argument('logfile', help='Path to the current log file.')
    p.add_argument('--start', metavar='TIMESTAMP', help='Show lines at or after this time.')
    p.add_argument('--end', metavar='TIMESTAMP', help='Show lines at or before this time.')
    p.add_argument('--no-gz', action='store_true', help='Skip compressed (.gz) rotated files.')
    p.add_argument('-n', '--number', action='store_true', help='Prefix lines with line numbers.')
    p.add_argument('--color', action='store_true', help='Highlight log levels with ANSI colours.')
    p.set_defaults(func=_cmd)


def _cmd(args: argparse.Namespace) -> None:
    run_rotate(
        logfile=args.logfile,
        start=getattr(args, 'start', None),
        end=getattr(args, 'end', None),
        no_gz=getattr(args, 'no_gz', False),
        number=getattr(args, 'number', False),
        color=getattr(args, 'color', False),
    )
