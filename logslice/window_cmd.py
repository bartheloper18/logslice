"""CLI sub-command: window — filter log lines to a sliding time window."""

from __future__ import annotations

import argparse
import datetime
import sys
from typing import Optional

from logslice.window import window_lines, window_file


def build_window_parser(
    parent: Optional[argparse._SubParsersAction] = None,
) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Emit only lines whose timestamp falls within the last N seconds."
    )
    if parent is not None:
        p = parent.add_parser("window", **kwargs)
    else:
        p = argparse.ArgumentParser(prog="logslice window", **kwargs)

    p.add_argument(
        "seconds",
        type=float,
        help="Width of the time window in seconds (e.g. 300 for the last 5 minutes).",
    )
    p.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Log file to read (default: stdin).",
    )
    p.add_argument(
        "--anchor",
        metavar="ISO8601",
        default=None,
        help="Upper bound of the window (default: now). Format: 2024-01-15T12:00:00Z",
    )
    return p


def run_window(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    if args.seconds <= 0:
        print("error: seconds must be positive", file=sys.stderr)
        return 1

    anchor = None
    if args.anchor:
        try:
            anchor = datetime.datetime.fromisoformat(args.anchor)
        except ValueError:
            print(f"error: invalid --anchor value: {args.anchor!r}", file=sys.stderr)
            return 1

    if args.file:
        lines = window_file(args.file, seconds=args.seconds, anchor=anchor)
    else:
        lines = window_lines(sys.stdin, seconds=args.seconds, anchor=anchor)

    for line in lines:
        out.write(line if line.endswith("\n") else line + "\n")

    return 0


def _cmd(argv=None):
    p = build_window_parser()
    args = p.parse_args(argv)
    raise SystemExit(run_window(args))
