"""Utilities for handling rotated log files (e.g. app.log, app.log.1, app.log.2.gz)."""

from __future__ import annotations

import gzip
import os
import re
from pathlib import Path
from typing import Iterator, List


_ROTATED_SUFFIX = re.compile(r'\.(\d+)(\.gz)?$')


def find_rotated_files(base: str | Path, include_gz: bool = True) -> List[Path]:
    """Return *base* plus any rotated siblings, ordered newest-first.

    Rotated files follow the common logrotate naming convention::

        app.log          <- current (index 0)
        app.log.1        <- previous
        app.log.2.gz     <- older, compressed

    Parameters
    ----------
    base:
        Path to the current (active) log file.
    include_gz:
        When *False*, compressed rotated files are excluded.
    """
    base = Path(base)
    parent = base.parent
    siblings: List[tuple[int, Path]] = []

    for entry in parent.iterdir():
        if entry == base:
            continue
        if not entry.name.startswith(base.name):
            continue
        m = _ROTATED_SUFFIX.search(entry.name[len(base.name):])
        if m is None:
            continue
        if not include_gz and entry.suffix == '.gz':
            continue
        siblings.append((int(m.group(1)), entry))

    siblings.sort(key=lambda t: t[0])
    return [base] + [p for _, p in siblings]


def open_rotated(path: Path):
    """Return a file-like object for *path*, transparently decompressing .gz."""
    if path.suffix == '.gz':
        return gzip.open(path, 'rt', encoding='utf-8', errors='replace')
    return path.open('r', encoding='utf-8', errors='replace')


def iter_rotated_lines(base: str | Path, include_gz: bool = True) -> Iterator[str]:
    """Yield lines from all rotated files in chronological order (oldest first)."""
    files = find_rotated_files(base, include_gz=include_gz)
    # oldest rotated file has the highest index — reverse so we go oldest→newest
    for path in reversed(files):
        with open_rotated(path) as fh:
            yield from fh
