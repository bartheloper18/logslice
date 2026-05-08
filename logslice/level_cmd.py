"""CLI sub-command: filter log lines by severity level."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from logslice.level_filter import LEVEL_ORDER, filter_by_level, filter_level_file


def build_level_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:  # noqa: SLF001
    kwargs = dict(
        prog="logslice level",
        description="Filter log lines by severity level.",
    )
    if sub is not None:
        p = sub.add_parser("level", **kwargs)
    else:
        p = argparse.ArgumentParser(**kwargs)

    p.add_argument(
        "min_level",
        metavar="MIN",
        help=f"Minimum severity level. Choices: {', '.join(LEVEL_ORDER)}",
    )
    p.add_argument(
        "--max",
        dest="max_level",
        metavar="MAX",
        default=None,
        help="Maximum severity level (inclusive). Defaults to no upper bound.",
    )
    p.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Input files. Reads from stdin when omitted.",
    )
    p.add_argument(
        "-o", "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    return p


def run_level(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    def _emit(lines):
        for line in filter_by_level(lines, args.min_level, args.max_level):
            out.write(line if line.endswith("\n") else line + "\n")

    if args.files:
        for path in args.files:
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    _emit(fh)
            except OSError as exc:
                print(f"logslice level: {exc}", file=sys.stderr)
                return 1
    else:
        _emit(sys.stdin)

    return 0


def _cmd(argv: List[str] | None = None) -> None:
    p = build_level_parser()
    args = p.parse_args(argv)
    sys.exit(run_level(args))


if __name__ == "__main__":  # pragma: no cover
    _cmd()
