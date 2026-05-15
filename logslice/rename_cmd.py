"""CLI sub-command: rename fields in structured log lines."""

from __future__ import annotations

import argparse
import sys
from typing import Dict

from logslice.rename import rename_lines, rename_file


def _parse_mapping(pairs) -> Dict[str, str]:
    """Convert a list of 'old=new' strings into a dict."""
    mapping: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"Invalid mapping '{pair}': expected old=new format"
            )
        old, _, new = pair.partition("=")
        if not old or not new:
            raise argparse.ArgumentTypeError(
                f"Invalid mapping '{pair}': both sides must be non-empty"
            )
        mapping[old] = new
    return mapping


def build_rename_parser(sub=None):
    kwargs = dict(
        description="Rename fields in JSON or key=value log lines."
    )
    if sub is not None:
        p = sub.add_parser("rename", **kwargs)
    else:
        p = argparse.ArgumentParser(**kwargs)

    p.add_argument(
        "mapping",
        nargs="+",
        metavar="OLD=NEW",
        help="Field rename mapping(s), e.g. msg=message level=severity",
    )
    p.add_argument(
        "--file", "-f",
        metavar="FILE",
        help="Input log file (default: stdin)",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output file (default: stdout)",
    )
    return p


def run_rename(ns: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    try:
        mapping = _parse_mapping(ns.mapping)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output = open(ns.output, "w", encoding="utf-8") if ns.output else out
    try:
        if ns.file:
            rename_file(ns.file, mapping, output)
        else:
            for line in rename_lines(sys.stdin, mapping):
                output.write(line)
    finally:
        if ns.output:
            output.close()

    return 0


def _cmd(argv=None):
    p = build_rename_parser()
    ns = p.parse_args(argv)
    sys.exit(run_rename(ns))


if __name__ == "__main__":
    _cmd()
