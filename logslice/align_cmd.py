"""CLI sub-command: align — pretty-print selected fields as aligned columns."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .align import align_lines, align_file


def build_align_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # noqa: F821
    p = sub.add_parser(
        "align",
        help="Align structured log fields into fixed-width columns.",
    )
    p.add_argument(
        "fields",
        nargs="+",
        metavar="FIELD",
        help="Field names to extract and align (JSON keys or key=value tokens).",
    )
    p.add_argument(
        "--sep",
        default="  ",
        metavar="SEP",
        help="Column separator (default: two spaces).",
    )
    p.add_argument(
        "--missing",
        default="-",
        metavar="VALUE",
        help="Placeholder for absent fields (default: -).",
    )
    p.add_argument(
        "file",
        nargs="?",
        default=None,
        metavar="FILE",
        help="Input file (default: stdin).",
    )
    p.set_defaults(func=_cmd)
    return p


def run_align(
    fields: List[str],
    file: str | None = None,
    sep: str = "  ",
    missing: str = "-",
    out=None,
) -> None:
    if out is None:
        out = sys.stdout
    if file:
        lines = align_file(file, fields, separator=sep, missing=missing)
    else:
        lines = align_lines(sys.stdin, fields, separator=sep, missing=missing)
    for line in lines:
        out.write(line)


def _cmd(ns: argparse.Namespace) -> None:
    run_align(
        fields=ns.fields,
        file=ns.file,
        sep=ns.sep,
        missing=ns.missing,
    )
