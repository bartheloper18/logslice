"""CLI sub-command: freq — show frequency distribution of log lines or field values."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .freq import format_freq, freq_lines


def build_freq_parser(sub=None) -> argparse.ArgumentParser:
    desc = "Show how often each unique line or field value appears."
    if sub is not None:
        p = sub.add_parser("freq", help=desc, description=desc)
    else:
        p = argparse.ArgumentParser(prog="logslice freq", description=desc)
    p.add_argument("files", nargs="*", metavar="FILE", help="Input files (default: stdin)")
    p.add_argument("-f", "--field", metavar="FIELD", default=None,
                   help="Count values of this JSON/KV field instead of whole lines")
    p.add_argument("-n", "--top", metavar="N", type=int, default=None,
                   help="Show only the top N entries")
    p.add_argument("--no-header", action="store_true", help="Suppress the header line")
    return p


def run_freq(args: argparse.Namespace, out=None) -> int:
    out = out or sys.stdout
    lines: List[str] = []

    if args.files:
        for path in args.files:
            try:
                with open(path, "r", errors="replace") as fh:
                    lines.extend(fh.readlines())
            except OSError as exc:
                sys.stderr.write(f"logslice freq: {exc}\n")
                return 1
    else:
        lines = sys.stdin.readlines()

    results = freq_lines(lines, field=args.field, top=args.top)
    if not results:
        return 0

    total = sum(c for _, c in results)
    if not args.no_header:
        label = args.field if args.field else "line"
        out.write(f"{'count':>6}  {'  %':>6}  {label}\n")
        out.write("-" * 40 + "\n")
    for line in format_freq(results, total):
        out.write(line)
    return 0


def _cmd(argv: Optional[List[str]] = None) -> None:
    p = build_freq_parser()
    args = p.parse_args(argv)
    sys.exit(run_freq(args))
