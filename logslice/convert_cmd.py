"""CLI sub-command: convert log format."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from logslice.convert import convert_lines, convert_file


def build_convert_parser(sub=None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Convert log lines between formats (json, kv, plain)."
    )
    if sub is not None:
        parser = sub.add_parser("convert", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument(
        "target",
        choices=["json", "kv", "plain"],
        help="Target output format.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Input log file (default: stdin).",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file (default: stdout).",
    )
    return parser


def run_convert(ns: argparse.Namespace, out=None) -> int:
    """Execute convert command; returns exit code."""
    if out is None:
        out = sys.stdout

    target: str = ns.target
    src: Optional[str] = ns.file
    dest: Optional[str] = getattr(ns, "output", None)

    writer = open(dest, "w", encoding="utf-8") if dest else out
    try:
        if src:
            convert_file(src, target, writer)
        else:
            for line in convert_lines(sys.stdin, target):
                writer.write(line)
    except ValueError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    finally:
        if dest and writer is not out:
            writer.close()
    return 0


def _cmd(argv=None):
    parser = build_convert_parser()
    ns = parser.parse_args(argv)
    sys.exit(run_convert(ns))


if __name__ == "__main__":  # pragma: no cover
    _cmd()
