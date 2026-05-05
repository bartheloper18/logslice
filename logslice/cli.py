"""Command-line interface for logslice."""

import argparse
import sys
from typing import Optional

from logslice.filter import filter_file
from logslice.detector import detect_format_from_file
from logslice.formats import list_formats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Filter log files by time range.",
    )
    parser.add_argument("file", nargs="?", help="Log file to filter (default: stdin)")
    parser.add_argument("--start", metavar="DATETIME", help="Start of time range (inclusive)")
    parser.add_argument("--end", metavar="DATETIME", help="End of time range (inclusive)")
    parser.add_argument(
        "--format",
        metavar="FORMAT",
        help="Force a specific log format instead of auto-detecting",
    )
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List all supported log formats and exit",
    )
    parser.add_argument(
        "--detect",
        action="store_true",
        help="Detect and print the log format of the given file, then exit",
    )
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_formats:
        for name, description in list_formats():
            print(f"  {name:<12} {description}")
        return 0

    if args.detect:
        if not args.file:
            print("error: --detect requires a FILE argument", file=sys.stderr)
            return 1
        fmt = detect_format_from_file(args.file)
        if fmt:
            print(f"Detected format: {fmt.name} — {fmt.description}")
        else:
            print("Could not detect a known log format.")
        return 0

    if not args.start and not args.end:
        parser.print_help()
        return 1

    try:
        if args.file:
            for line in filter_file(args.file, start=args.start, end=args.end):
                sys.stdout.write(line)
        else:
            from logslice.filter import filter_lines
            for line in filter_lines(sys.stdin, start=args.start, end=args.end):
                sys.stdout.write(line)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
