"""CLI sub-command: sort log lines by timestamp or field."""

from __future__ import annotations

import argparse
import sys

from logslice.sort import sort_lines, sort_file


def build_sort_parser(sub=None) -> argparse.ArgumentParser:
    desc = "Sort log lines by timestamp or a named field."
    if sub is not None:
        p = sub.add_parser("sort", help=desc, description=desc)
    else:
        p = argparse.ArgumentParser(prog="logslice sort", description=desc)
    p.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Input log file (default: stdin).",
    )
    p.add_argument(
        "-k", "--key",
        default="timestamp",
        metavar="KEY",
        help="Sort key: 'timestamp' (default) or a field name.",
    )
    p.add_argument(
        "-r", "--reverse",
        action="store_true",
        default=False,
        help="Sort in descending order.",
    )
    return p


def run_sort(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    if args.file:
        sort_file(args.file, out, key=args.key, reverse=args.reverse)
    else:
        lines = sys.stdin.readlines()
        for line in sort_lines(lines, key=args.key, reverse=args.reverse):
            out.write(line)
    return 0


def _cmd(argv=None):
    p = build_sort_parser()
    args = p.parse_args(argv)
    raise SystemExit(run_sort(args))


if __name__ == "__main__":  # pragma: no cover
    _cmd()
