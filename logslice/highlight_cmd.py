"""Command-level wrappers for highlight/colorize operations on log files."""

from __future__ import annotations

import argparse
import sys
from typing import IO, List, Optional

from logslice.highlighter import highlight_line, supports_color


def build_highlight_parser(sub=None) -> argparse.ArgumentParser:
    """Return an ArgumentParser for the highlight sub-command."""
    kwargs = dict(
        description="Colorize log levels and timestamps in a log file or stdin."
    )
    if sub is not None:
        parser = sub.add_parser("highlight", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Path to log file (default: stdin).",
    )
    parser.add_argument(
        "--no-color",
        dest="no_color",
        action="store_true",
        default=False,
        help="Disable ANSI color output even when the terminal supports it.",
    )
    parser.add_argument(
        "--levels-only",
        dest="levels_only",
        action="store_true",
        default=False,
        help="Only highlight log-level tokens; skip timestamp highlighting.",
    )
    return parser


def run_highlight(
    args: argparse.Namespace,
    out: IO[str] = sys.stdout,
) -> int:
    """Execute the highlight command.  Returns an exit code."""
    use_color = (not args.no_color) and supports_color(out)

    if args.file:
        try:
            fh = open(args.file, "r", encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"logslice highlight: {exc}", file=sys.stderr)
            return 1
        lines = fh
    else:
        lines = sys.stdin

    try:
        for raw in lines:
            highlighted = highlight_line(
                raw,
                color=use_color,
                timestamps=(not args.levels_only),
            )
            out.write(highlighted if highlighted.endswith("\n") else highlighted + "\n")
    finally:
        if args.file:
            lines.close()  # type: ignore[union-attr]

    return 0


def _cmd(argv: Optional[List[str]] = None) -> None:  # pragma: no cover
    parser = build_highlight_parser()
    args = parser.parse_args(argv)
    sys.exit(run_highlight(args))


if __name__ == "__main__":  # pragma: no cover
    _cmd()
