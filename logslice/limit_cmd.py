"""CLI sub-command: limit — emit log lines up to a byte budget."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .limit import limit_lines, limit_file


_UNITS = {"b": 1, "k": 1024, "m": 1024 ** 2, "g": 1024 ** 3}


def _parse_size(value: str) -> int:
    """Parse a human-friendly size string such as ``512k`` or ``10m``."""
    value = value.strip().lower()
    if value[-1] in _UNITS:
        return int(value[:-1]) * _UNITS[value[-1]]
    return int(value)


def build_limit_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Emit log lines until a byte budget is exhausted.",
    )
    if sub is not None:
        p = sub.add_parser("limit", **kwargs)
    else:
        p = argparse.ArgumentParser(prog="logslice limit", **kwargs)

    p.add_argument(
        "size",
        help="Maximum output size, e.g. 512, 64k, 10m.",
    )
    p.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Input file (default: stdin).",
    )
    p.add_argument(
        "--truncate",
        action="store_true",
        default=False,
        help="Truncate the last line instead of dropping it.",
    )
    return p


def run_limit(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    try:
        max_bytes = _parse_size(args.size)
    except (ValueError, IndexError):
        print(f"logslice limit: invalid size '{args.size}'", file=sys.stderr)
        return 1

    if args.file:
        limit_file(args.file, max_bytes, out, truncate=args.truncate)
    else:
        for line in limit_lines(sys.stdin, max_bytes, truncate=args.truncate):
            out.write(line)
    return 0


def _cmd(argv: List[str]) -> int:
    p = build_limit_parser()
    args = p.parse_args(argv)
    return run_limit(args)
