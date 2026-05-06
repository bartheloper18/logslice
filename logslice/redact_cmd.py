"""CLI command implementation for the redact feature."""

import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional

from logslice.redact import (
    BUILTIN_PATTERNS,
    compile_redact_patterns,
    redact_file,
    redact_lines,
)


def build_redact_parser(sub=None) -> ArgumentParser:
    kwargs = dict(
        description="Redact sensitive data from log lines.",
        prog="logslice redact",
    )
    parser = sub.add_parser("redact", **kwargs) if sub else ArgumentParser(**kwargs)
    parser.add_argument("files", nargs="*", metavar="FILE", help="Input log files (stdin if omitted)")
    parser.add_argument("-p", "--pattern", dest="patterns", action="append", default=[], metavar="REGEX",
                        help="Custom regex pattern to redact (repeatable)")
    parser.add_argument("-b", "--builtin", dest="builtins", action="append", default=[],
                        choices=list(BUILTIN_PATTERNS), metavar="NAME",
                        help="Built-in pattern name to redact (%(choices)s)")
    parser.add_argument("-m", "--mask", default="[REDACTED]", metavar="TEXT",
                        help="Replacement text (default: [REDACTED])")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Case-insensitive matching")
    return parser


def run_redact(args: Namespace, out=None) -> int:
    out = out or sys.stdout
    try:
        compiled = compile_redact_patterns(
            args.patterns,
            builtins=args.builtins,
            ignore_case=args.ignore_case,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not compiled:
        print("error: specify at least one --pattern or --builtin", file=sys.stderr)
        return 1

    if args.files:
        for path in args.files:
            try:
                for line in redact_file(path, compiled, args.mask):
                    out.write(line if line.endswith("\n") else line + "\n")
            except OSError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 1
    else:
        for line in redact_lines(sys.stdin, compiled, args.mask):
            out.write(line if line.endswith("\n") else line + "\n")

    return 0


def _cmd(argv: Optional[List[str]] = None) -> None:
    parser = build_redact_parser()
    args = parser.parse_args(argv)
    sys.exit(run_redact(args))


if __name__ == "__main__":
    _cmd()
