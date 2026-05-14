"""CLI sub-command: template – reshape log lines with a format template."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from logslice.template import template_lines, template_file


def build_template_parser(sub: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    desc = "Reshape log lines using a placeholder template."
    if sub is not None:
        p = sub.add_parser("template", help=desc, description=desc)
    else:
        p = argparse.ArgumentParser(prog="logslice template", description=desc)

    p.add_argument(
        "template",
        metavar="TEMPLATE",
        help="Format string, e.g. '{timestamp} [{level}] {message}'",
    )
    p.add_argument(
        "file",
        metavar="FILE",
        nargs="?",
        default=None,
        help="Input log file (default: stdin).",
    )
    p.add_argument(
        "-o", "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    return p


def run_template(ns: argparse.Namespace, out=None) -> int:
    """Execute the template sub-command; return exit code."""
    import io

    if out is None:
        if ns.output:
            out = open(ns.output, "w", encoding="utf-8")
        else:
            out = sys.stdout

    try:
        if ns.file:
            template_file(ns.file, ns.template, out=out)
        else:
            for rendered in template_lines(sys.stdin, ns.template):
                out.write(rendered)
    except FileNotFoundError as exc:
        print(f"logslice template: {exc}", file=sys.stderr)
        return 1
    finally:
        if ns.output and out is not sys.stdout:
            out.close()

    return 0


def _cmd(argv=None) -> None:
    p = build_template_parser()
    ns = p.parse_args(argv)
    sys.exit(run_template(ns))


if __name__ == "__main__":  # pragma: no cover
    _cmd()
