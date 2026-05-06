"""Portable bookmark store with optional path normalization and migration."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterator

from logslice.bookmark import DEFAULT_BOOKMARK_FILE, _load, _save


def export_bookmarks(
    dest: Path,
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
    relative_to: str | None = None,
) -> int:
    """Export bookmarks to *dest* as JSON, optionally making paths relative.

    Returns the number of bookmarks exported.
    """
    data = _load(bookmark_file)
    if relative_to:
        base = os.path.abspath(relative_to)
        for info in data.values():
            try:
                info["file"] = os.path.relpath(info["file"], base)
            except ValueError:
                pass  # different drive on Windows — keep absolute
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return len(data)


def import_bookmarks(
    src: Path,
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
    overwrite: bool = False,
) -> tuple[int, int]:
    """Import bookmarks from *src* into the active bookmark file.

    Returns (imported, skipped) counts.
    """
    with src.open("r", encoding="utf-8") as fh:
        incoming = json.load(fh)
    existing = _load(bookmark_file)
    imported = skipped = 0
    for name, info in incoming.items():
        if name in existing and not overwrite:
            skipped += 1
            continue
        existing[name] = info
        imported += 1
    _save(existing, bookmark_file)
    return imported, skipped


def iter_bookmarks(
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
) -> Iterator[tuple[str, str, int]]:
    """Yield (name, filepath, line_number) tuples for every saved bookmark."""
    data = _load(bookmark_file)
    for name, info in sorted(data.items()):
        yield name, info["file"], info["line"]


def purge_missing(
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
) -> list[str]:
    """Remove bookmarks whose target file no longer exists.

    Returns list of purged bookmark names.
    """
    data = _load(bookmark_file)
    purged = [name for name, info in data.items() if not os.path.exists(info["file"])]
    for name in purged:
        del data[name]
    if purged:
        _save(data, bookmark_file)
    return purged
