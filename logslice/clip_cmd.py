"""clip_cmd.py – CLI glue for the clip feature."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .clip import clip_lines, clip_file


def build_clip_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Return (or register) the argument parser for the *clip* sub-command."""
    kwargs = dict(
        prog="logslice clip",
        description="Extract a line-number range from a log file or stdin.",
    )
    parser = sub.add_parser("clip", **kwargs) if sub else argparse.ArgumentParser(**kwargs)
    parser.add_argument("start", type=int, help="First line to include (1-based).")
    parser.add_argument(
        "end",
        type=int,
        nargs="?",
        default=None,
        help="Last line to include (1-based, inclusive).  Omit to read until EOF.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        metavar="FILE",
        help="Input file.  Reads from stdin when omitted.",
    )
    return parser


def run_clip(ns: argparse.Namespace, out=None) -> int:
    """Execute the clip command described by *ns*.

    Returns an exit code (0 = success, 1 = error).
    """
    import sys as _sys

    sink = out or _sys.stdout
    try:
        if ns.file:
            clip_file(ns.file, start=ns.start, end=ns.end, out=sink)
        else:
            for line in clip_lines(_sys.stdin, start=ns.start, end=ns.end):
                sink.write(line)
    except ValueError as exc:
        print(f"clip: {exc}", file=_sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"clip: file not found: {ns.file}", file=_sys.stderr)
        return 1
    return 0


def _cmd(argv: Optional[List[str]] = None) -> None:  # pragma: no cover
    parser = build_clip_parser()
    ns = parser.parse_args(argv)
    raise SystemExit(run_clip(ns))
