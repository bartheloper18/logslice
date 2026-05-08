"""CLI sub-command: logslice rate — show event rate over time windows."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.rate import bucket_lines, format_rate


def build_rate_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="logslice rate",
        description="Show log event rate grouped into fixed time windows.",
    )
    parser = (
        sub.add_parser("rate", **kwargs)  # type: ignore[arg-type]
        if sub is not None
        else argparse.ArgumentParser(**kwargs)  # type: ignore[arg-type]
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Log file to analyse (default: stdin).",
    )
    parser.add_argument(
        "-w",
        "--window",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Bucket window in seconds (default: 60).",
    )
    parser.add_argument(
        "--label",
        default="events",
        help="Label for the event noun in output (default: events).",
    )
    return parser


def run_rate(args: argparse.Namespace, out=sys.stdout) -> int:
    """Execute the rate sub-command.

    Returns:
        Exit code (0 on success, 1 on error).
    """
    if args.window < 1:
        out.write("error: --window must be >= 1\n")
        return 1

    if args.file:
        try:
            fh = open(args.file, "r", errors="replace")
        except OSError as exc:
            out.write(f"error: {exc}\n")
            return 1
    else:
        fh = sys.stdin

    try:
        lines = fh.readlines()
    finally:
        if args.file:
            fh.close()

    buckets = bucket_lines(lines, window_seconds=args.window)
    if not buckets:
        out.write("(no timestamped lines found)\n")
        return 0

    for row in format_rate(buckets, window_seconds=args.window, label=args.label):
        out.write(row + "\n")
    return 0


def _cmd(argv: Optional[List[str]] = None) -> None:  # pragma: no cover
    parser = build_rate_parser()
    args = parser.parse_args(argv)
    sys.exit(run_rate(args))
