"""CLI command: logslice annotate — add metadata prefixes to log lines."""

from __future__ import annotations

import argparse
import sys
from typing import IO

from logslice.annotate import annotate_lines, format_annotated


def build_annotate_parser(subparsers=None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Annotate log lines with line numbers, elapsed time, or inter-line deltas."
    )
    if subparsers is not None:
        parser = subparsers.add_parser("annotate", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="logslice annotate", **kwargs)

    parser.add_argument("file", nargs="?", default="-", help="Input file (default: stdin)")
    parser.add_argument("-n", "--lineno", action="store_true", default=True,
                        help="Prefix each line with its line number (default: on)")
    parser.add_argument("--no-lineno", dest="lineno", action="store_false",
                        help="Disable line number prefix")
    parser.add_argument("-e", "--elapsed", action="store_true", default=False,
                        help="Show elapsed ms since first timestamped line")
    parser.add_argument("-d", "--delta", action="store_true", default=False,
                        help="Show ms delta between consecutive timestamped lines")
    parser.add_argument("-o", "--output", default="-", metavar="FILE",
                        help="Output file (default: stdout)")
    return parser


def run_annotate(args: argparse.Namespace, *, out: IO[str] = sys.stdout) -> int:
    show_lineno = args.lineno
    show_elapsed = args.elapsed
    show_delta = args.delta

    def _process(lines):
        for ann in annotate_lines(
            lines,
            show_lineno=show_lineno,
            show_elapsed=show_elapsed,
            show_delta=show_delta,
        ):
            out.write(format_annotated(
                ann,
                show_lineno=show_lineno,
                show_elapsed=show_elapsed,
                show_delta=show_delta,
            ))

    target = getattr(args, "file", "-")
    if target == "-":
        _process(sys.stdin)
    else:
        try:
            with open(target, "r", encoding="utf-8", errors="replace") as fh:
                _process(fh)
        except FileNotFoundError:
            print(f"annotate: file not found: {target}", file=sys.stderr)
            return 1
    return 0


def _cmd(argv=None):
    parser = build_annotate_parser()
    args = parser.parse_args(argv)
    raise SystemExit(run_annotate(args))


if __name__ == "__main__":  # pragma: no cover
    _cmd()
