"""CLI sub-command: cast — coerce a JSON field to a given type."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .cast import cast_lines, cast_file


def build_cast_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:  # noqa: SLF001
    kwargs = dict(
        prog="logslice cast",
        description="Coerce a JSON field value to int, float, bool, or str.",
    )
    parser = sub.add_parser("cast", **kwargs) if sub else argparse.ArgumentParser(**kwargs)
    parser.add_argument("field", help="Field name to cast")
    parser.add_argument(
        "type",
        choices=["int", "float", "bool", "str"],
        help="Target type",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Input file (default: stdin)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    return parser


def run_cast(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    if args.file:
        lines = cast_file(args.file, args.field, args.type)
    else:
        lines = cast_lines(sys.stdin, args.field, args.type)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            for line in lines:
                fh.write(line if line.endswith("\n") else line + "\n")
    else:
        for line in lines:
            out.write(line if line.endswith("\n") else line + "\n")

    return 0


def _cmd(argv: List[str] | None = None) -> None:  # pragma: no cover
    parser = build_cast_parser()
    args = parser.parse_args(argv)
    sys.exit(run_cast(args))
