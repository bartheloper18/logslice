"""pivot_cmd.py – CLI entry-point for the pivot sub-command."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from logslice.pivot import format_pivot, pivot_lines


def build_pivot_parser(sub=None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Transpose log fields into a columnar summary table."
    )
    if sub is not None:
        parser = sub.add_parser("pivot", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice pivot", **kwargs)

    parser.add_argument(
        "key",
        help="Field name to group by (must exist in JSON or key=value lines).",
    )
    parser.add_argument(
        "--value",
        metavar="FIELD",
        default=None,
        help="Numeric field to aggregate alongside the count.",
    )
    parser.add_argument(
        "--agg",
        choices=["count", "sum", "mean"],
        default="count",
        help="Aggregation mode when --value is given (default: count).",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Log file to read (defaults to stdin).",
    )
    return parser


def run_pivot(ns: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    if ns.file:
        try:
            fh = open(ns.file, "r", errors="replace")
        except OSError as exc:
            print(f"logslice pivot: {exc}", file=sys.stderr)
            return 1
    else:
        fh = sys.stdin

    try:
        data = pivot_lines(fh, key=ns.key, value=ns.value, agg=ns.agg)
    finally:
        if ns.file:
            fh.close()

    out.write(format_pivot(data, value=ns.value))
    return 0


def _cmd(argv=None) -> None:
    parser = build_pivot_parser()
    ns = parser.parse_args(argv)
    sys.exit(run_pivot(ns))


if __name__ == "__main__":  # pragma: no cover
    _cmd()
