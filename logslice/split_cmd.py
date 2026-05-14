"""CLI sub-command: split — fan-out log lines into per-bucket files."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Optional

from logslice.split import split_lines, split_file


def build_split_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="logslice split",
        description="Fan-out log lines into separate files based on a field or regex group.",
    )
    parser = sub.add_parser("split", **kwargs) if sub else argparse.ArgumentParser(**kwargs)
    parser.add_argument("file", nargs="?", help="Input file (default: stdin)")
    parser.add_argument("-o", "--output-dir", default=".", metavar="DIR",
                        help="Directory to write output files (default: current dir)")
    parser.add_argument("-p", "--prefix", default="split",
                        help="Filename prefix for output files (default: split)")
    parser.add_argument("-s", "--suffix", default=".log",
                        help="Filename suffix/extension (default: .log)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--field", metavar="FIELD",
                       help="Structured field name to split on (JSON or key=value)")
    group.add_argument("-e", "--pattern", metavar="REGEX",
                       help="Regex with a capture group whose value is used as the bucket key")
    return parser


def run_split(args: argparse.Namespace) -> int:
    pattern = None
    if args.pattern:
        try:
            pattern = re.compile(args.pattern)
        except re.error as exc:
            print(f"logslice split: invalid pattern: {exc}", file=sys.stderr)
            return 1

    if args.file:
        counts = split_file(
            args.file,
            output_dir=args.output_dir,
            prefix=args.prefix,
            field=args.field,
            pattern=pattern,
            suffix=args.suffix,
        )
    else:
        counts = split_lines(
            sys.stdin,
            output_dir=args.output_dir,
            prefix=args.prefix,
            field=args.field,
            pattern=pattern,
            suffix=args.suffix,
        )

    for key, count in sorted(counts.items()):
        print(f"{key}: {count} line(s)")
    return 0


def _cmd(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = build_split_parser(sub)
    p.set_defaults(func=run_split)
