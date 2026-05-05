"""Optional pager integration for long log output."""

import os
import subprocess
import sys
from contextlib import contextmanager
from typing import Generator, Optional, TextIO


DEFAULT_PAGER = "less -R"


def get_pager_cmd() -> str:
    """Return the pager command from environment or default."""
    return os.environ.get("PAGER", DEFAULT_PAGER)


def should_use_pager(force: Optional[bool] = None) -> bool:
    """Determine whether to pipe output through a pager."""
    if force is not None:
        return force
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


@contextmanager
def pager_context(use_pager: bool = True) -> Generator[TextIO, None, None]:
    """
    Context manager that yields either a pager subprocess stdin
    or sys.stdout depending on use_pager.

    Usage:
        with pager_context(use_pager=True) as out:
            write_output(lines, output=out)
    """
    if not use_pager:
        yield sys.stdout
        return

    pager_cmd = get_pager_cmd()
    try:
        proc = subprocess.Popen(
            pager_cmd,
            shell=True,
            stdin=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            yield proc.stdin  # type: ignore[misc]
        finally:
            if proc.stdin:
                proc.stdin.close()
            proc.wait()
    except (OSError, BrokenPipeError):
        yield sys.stdout
