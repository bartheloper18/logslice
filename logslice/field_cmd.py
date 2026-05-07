"""CLI sub-command: logslice field — filter or inspect log fields."""

import argparse
import sys
from typing import List, Optional

from logslice.field import filter_by_field, get_field


def build_field_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    kwargs = dict(
        prog="logslice field",
        description="Filter structured log lines by field value.",
    )
    if sub is not None:
        p = sub.add_parser("field", **kwargs)
    else:
        p = argparse.ArgumentParser(**kwargs)

    p.add_argument("field", help="Field name to inspect or filter on")
    p.add_argument("value", nargs="?", help="Required field value (omit to print field values)")
    p.add_argument("file", nargs="?", help="Input file (default: stdin)")
    p.add_argument("-i", "--ignore-case", action="store_true", help="Case-insensitive comparison")
    return p


def run_field(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    src = open(args.file) if getattr(args, "file", None) else sys.stdin
    try:
        lines: List[str] = src.readlines()
    finally:
        if src is not sys.stdin:
            src.close()

    if args.value is None:
        # Print extracted field values
        for line in lines:
            val = get_field(line.rstrip("\n"), args.field)
            if val is not None:
                out.write(val + "\n")
        return 0

    filtered = filter_by_field(
        [l.rstrip("\n") for l in lines],
        args.field,
        args.value,
        ignore_case=args.ignore_case,
    )
    for line in filtered:
        out.write(line + "\n")
    return 0


def _cmd(argv=None):
    p = build_field_parser()
    args = p.parse_args(argv)
    sys.exit(run_field(args))


if __name__ == "__main__":
    _cmd()
