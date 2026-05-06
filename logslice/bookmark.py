"""Bookmark support: save and restore named positions in log files."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_BOOKMARK_FILE = Path.home() / ".logslice_bookmarks.json"


def _load(bookmark_file: Path) -> dict:
    if bookmark_file.exists():
        with bookmark_file.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _save(data: dict, bookmark_file: Path) -> None:
    with bookmark_file.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def set_bookmark(
    name: str,
    filepath: str,
    line_number: int,
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
) -> None:
    """Save a named bookmark pointing to a file and line number."""
    data = _load(bookmark_file)
    data[name] = {"file": os.path.abspath(filepath), "line": line_number}
    _save(data, bookmark_file)


def get_bookmark(
    name: str,
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
) -> Optional[dict]:
    """Return bookmark dict with 'file' and 'line', or None if not found."""
    data = _load(bookmark_file)
    return data.get(name)


def delete_bookmark(
    name: str,
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
) -> bool:
    """Delete a bookmark by name. Returns True if it existed."""
    data = _load(bookmark_file)
    if name in data:
        del data[name]
        _save(data, bookmark_file)
        return True
    return False


def list_bookmarks(
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
) -> dict:
    """Return all bookmarks as a dict."""
    return _load(bookmark_file)


def read_from_bookmark(
    name: str,
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
) -> list[str]:
    """Read all lines from the bookmarked file starting at the saved line."""
    bm = get_bookmark(name, bookmark_file)
    if bm is None:
        raise KeyError(f"Bookmark {name!r} not found")
    filepath = bm["file"]
    start_line = bm["line"]
    with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    return lines[start_line:]
