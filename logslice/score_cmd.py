"""CLI command: logslice score — rank log lines by keyword relevance."""
from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Optional

from logslice.score import format_scored, score_file, score_lines


def _parse_weights(specs: List[str]) -> Dict[str, float]:
    """Parse 'PATTERN:WEIGHT' strings into a dict."""
    weights: Dict[str, float] = {}
    for spec in specs:
        if ":" not in spec:
            raise argparse.ArgumentTypeError(
                f"Weight spec must be PATTERN:WEIGHT, got: {spec!r}"
            )
        pattern, _, raw_weight = spec.rpartition(":")
        try:
            weights[pattern] = float(raw_weight)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Weight must be a number, got: {raw_weight!r}"
            )
    return weights


def build_score_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice score",
        description="Rank log lines by weighted keyword relevance.",
    )
    p.add_argument(
        "weights",
        nargs="+",
        metavar="PATTERN:WEIGHT",
        help="Keyword pattern and numeric weight, e.g. 'error:2.0'",
    )
    p.add_argument("--file", "-f", metavar="FILE", help="Input file (default: stdin)")
    p.add_argument(
        "--threshold", "-t", type=float, default=0.0, metavar="N",
        help="Minimum score to include a line (default: 0.0)",
    )
    p.add_argument(
        "--top", "-n", type=int, default=None, metavar="N",
        help="Only show the top N results",
    )
    p.add_argument(
        "--no-score", action="store_true", help="Suppress score column"
    )
    p.add_argument(
        "--no-lineno", action="store_true", help="Suppress line-number column"
    )
    return p


def run_score(ns: argparse.Namespace, out=None) -> int:
    if out is None:
        out = sys.stdout
    try:
        weights = _parse_weights(ns.weights)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if ns.file:
        try:
            with open(ns.file) as fh:
                results = score_file(fh, weights, threshold=ns.threshold, top_n=ns.top)
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    else:
        results = score_lines(
            sys.stdin, weights, threshold=ns.threshold, top_n=ns.top
        )

    for sl in results:
        print(format_scored(sl, show_score=not ns.no_score, show_lineno=not ns.no_lineno), file=out)
    return 0


def _cmd(argv: Optional[List[str]] = None) -> None:
    p = build_score_parser()
    ns = p.parse_args(argv)
    sys.exit(run_score(ns))
