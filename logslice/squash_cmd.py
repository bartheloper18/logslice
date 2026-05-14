"""CLI sub-command: squash – collapse repeated log lines."""
from __future__ import annotations

import argparse
import sys
from typing import Sequence

from logslice.squash import squash_file, squash_lines


def build_squash_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "squash",
        help="Collapse consecutive similar lines into one summary line.",
        description=(
            "Lines that differ only in numeric tokens are treated as identical. "
            "Consecutive runs of such lines are replaced by a single representative "
            "line annotated with the repetition count."
        ),
    )
    p.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Input log file (default: stdin).",
    )
    p.add_argument(
        "-n",
        "--min-repeat",
        type=int,
        default=2,
        metavar="N",
        help="Minimum repetitions before collapsing (default: 2).",
    )
    p.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    p.set_defaults(func=_cmd)
    return p


def run_squash(
    file: str | None,
    *,
    min_repeat: int = 2,
    out=None,
) -> None:
    """Run squash and write results to *out* (default: stdout)."""
    if out is None:
        out = sys.stdout
    if file:
        lines = squash_file(file, min_repeat=min_repeat)
    else:
        lines = squash_lines(sys.stdin, min_repeat=min_repeat)
    for line in lines:
        out.write(line)


def _cmd(args: argparse.Namespace) -> None:
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            run_squash(args.file, min_repeat=args.min_repeat, out=fh)
    else:
        run_squash(args.file, min_repeat=args.min_repeat)
