"""CLI sub-command: unique — emit lines with distinct field values."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from logslice.unique import unique_lines, unique_values


def build_unique_parser(sub: "argparse._SubParsersAction") -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "unique",
        help="Filter log lines to unique values of a field (or full line).",
    )
    p.add_argument(
        "field",
        nargs="?",
        default=None,
        help="Structured field to deduplicate on (JSON key or kv key). "
             "Omit to deduplicate on full line text.",
    )
    p.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Input file (default: stdin).",
    )
    p.add_argument(
        "--values-only",
        action="store_true",
        default=False,
        help="Print only the distinct field values, not the full lines.",
    )
    p.add_argument(
        "--ignore-case", "-i",
        action="store_true",
        default=False,
        help="Case-insensitive comparison of field values.",
    )
    p.set_defaults(func=_cmd)
    return p


def run_unique(
    field: Optional[str],
    source,
    out,
    values_only: bool = False,
    ignore_case: bool = False,
) -> int:
    if values_only and field:
        from logslice.unique import unique_values
        for value in unique_values(source, field, ignore_case=ignore_case):
            out.write(value + "\n")
    else:
        for line in unique_lines(source, field=field, ignore_case=ignore_case):
            text = line if line.endswith("\n") else line + "\n"
            out.write(text)
    return 0


def _cmd(ns: argparse.Namespace) -> int:
    src = open(ns.file, "r", encoding="utf-8", errors="replace") if ns.file else sys.stdin
    try:
        return run_unique(
            field=ns.field,
            source=src,
            out=sys.stdout,
            values_only=ns.values_only,
            ignore_case=ns.ignore_case,
        )
    finally:
        if ns.file:
            src.close()
