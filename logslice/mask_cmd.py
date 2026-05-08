"""CLI sub-command: mask — hide sensitive values in log lines."""

from __future__ import annotations

import argparse
import re
import sys
from typing import List, Optional

from logslice.mask import mask_lines


def build_mask_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Mask sensitive values in log lines."
    if subparsers is not None:
        parser = subparsers.add_parser("mask", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="logslice mask", description=description)

    parser.add_argument("file", nargs="?", help="Input file (default: stdin)")
    parser.add_argument("-p", "--pattern", metavar="REGEX",
                        help="Regex pattern whose matches are masked")
    parser.add_argument("-f", "--field", metavar="KEY",
                        help="key=value field name whose value is masked")
    parser.add_argument("--placeholder", default="***",
                        help="Replacement string (default: %(default)s)")
    parser.add_argument("-o", "--output", metavar="FILE",
                        help="Write output to FILE instead of stdout")
    return parser


def run_mask(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    if not args.pattern and not args.field:
        print("error: at least one of --pattern or --field is required", file=sys.stderr)
        return 1

    compiled: Optional[re.Pattern] = None  # type: ignore[type-arg]
    if args.pattern:
        try:
            compiled = re.compile(args.pattern)
        except re.error as exc:
            print(f"error: invalid regex: {exc}", file=sys.stderr)
            return 1

    src = open(args.file) if args.file else sys.stdin
    dest = open(args.output, "w") if getattr(args, "output", None) else out

    try:
        for line in mask_lines(src, pattern=compiled, field=args.field,
                               placeholder=args.placeholder):
            dest.write(line)
    finally:
        if args.file:
            src.close()
        if getattr(args, "output", None):
            dest.close()

    return 0


def _cmd(argv: List[str] | None = None) -> None:
    parser = build_mask_parser()
    args = parser.parse_args(argv)
    sys.exit(run_mask(args))


if __name__ == "__main__":
    _cmd()
