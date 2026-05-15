"""CLI sub-command: column — extract and display structured fields as columns."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .column import column_file, format_columns


def build_column_parser(sub=None) -> argparse.ArgumentParser:
    desc = "Extract fields from structured logs and display as aligned columns."
    if sub is not None:
        p = sub.add_parser("column", help=desc, description=desc)
    else:
        p = argparse.ArgumentParser(prog="logslice column", description=desc)
    p.add_argument("fields", nargs="+", metavar="FIELD", help="Field names to extract")
    p.add_argument("--file", "-f", metavar="PATH", help="Input file (default: stdin)")
    p.add_argument("--separator", "-s", default="  ", metavar="SEP",
                   help="Column separator (default: two spaces)")
    p.add_argument("--missing", default="-", metavar="STR",
                   help="Placeholder for missing fields (default: -)")
    p.add_argument("--no-header", dest="no_header", action="store_true",
                   help="Suppress the header row")
    return p


def run_column(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    kwargs = dict(
        separator=args.separator,
        missing=args.missing,
        header=not args.no_header,
    )

    try:
        if args.file:
            lines = column_file(args.file, args.fields, **kwargs)
        else:
            lines = format_columns(sys.stdin, args.fields, **kwargs)

        for line in lines:
            out.write(line)
    except FileNotFoundError as exc:
        sys.stderr.write(f"logslice column: {exc}\n")
        return 1
    return 0


def _cmd(argv: Optional[List[str]] = None) -> None:
    p = build_column_parser()
    args = p.parse_args(argv)
    sys.exit(run_column(args))


if __name__ == "__main__":
    _cmd()
