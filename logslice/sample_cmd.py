"""CLI sub-command: sample — emit a subset of log lines."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from logslice.sample import sample_file


def build_sample_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "sample",
        help="Emit a deterministic or random subset of log lines.",
    )
    p.add_argument("file", nargs="?", help="Log file (default: stdin).")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--every",
        metavar="N",
        type=int,
        help="Keep every Nth line.",
    )
    mode.add_argument(
        "--fraction",
        metavar="F",
        type=float,
        help="Keep each line with probability F (0 < F <= 1).",
    )
    p.add_argument(
        "--seed",
        metavar="S",
        type=int,
        default=None,
        help="RNG seed for reproducible --fraction sampling.",
    )
    return p


def run_sample(args: argparse.Namespace, out=None) -> int:
    """Execute the sample sub-command.  Returns an exit code."""
    if out is None:
        out = sys.stdout

    every = args.every or 0
    fraction = args.fraction or 0.0

    try:
        if args.file:
            with open(args.file) as fh:
                for line in sample_file(fh, every=every, fraction=fraction, seed=args.seed):
                    out.write(line)
        else:
            for line in sample_file(sys.stdin, every=every, fraction=fraction, seed=args.seed):
                out.write(line)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


def _cmd(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="logslice-sample")
    sub = parser.add_subparsers(dest="cmd")
    build_sample_parser(sub)
    args = parser.parse_args(argv)
    sys.exit(run_sample(args))
