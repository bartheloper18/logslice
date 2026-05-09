"""CLI sub-command: chunk — split log input into numbered segments."""

from __future__ import annotations

import argparse
import sys
from typing import List

from logslice.chunk import chunk_by_count, chunk_by_seconds
from logslice.parser import extract_timestamp


def build_chunk_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser("chunk", help="Split log lines into chunks")
    p.add_argument("file", nargs="?", default="-", help="Input file (default: stdin)")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--size", type=int, metavar="N",
                       help="Lines per chunk")
    group.add_argument("-s", "--seconds", type=float, metavar="S",
                       help="Time window per chunk in seconds")
    p.add_argument("--prefix", default="chunk",
                   help="Label prefix printed before each chunk (default: 'chunk')")
    p.set_defaults(func=_cmd)
    return p


def run_chunk(args: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout

    if args.file == "-":
        lines: List[str] = sys.stdin.readlines()
    else:
        try:
            with open(args.file, "r", errors="replace") as fh:
                lines = fh.readlines()
        except OSError as exc:
            print(f"chunk: {exc}", file=sys.stderr)
            return 1

    if args.size is not None:
        chunks = chunk_by_count(lines, args.size)
    else:
        chunks = chunk_by_seconds(lines, args.seconds)

    for idx, chunk in enumerate(chunks, 1):
        out.write(f"--- {args.prefix} {idx} ---\n")
        for line in chunk:
            out.write(line if line.endswith("\n") else line + "\n")

    return 0


def _cmd(args: argparse.Namespace) -> None:
    sys.exit(run_chunk(args))
