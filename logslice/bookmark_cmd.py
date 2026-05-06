"""CLI command handler for bookmark sub-commands."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from logslice.bookmark import (
    DEFAULT_BOOKMARK_FILE,
    delete_bookmark,
    get_bookmark,
    list_bookmarks,
    set_bookmark,
)


def run_bookmark(
    action: str,
    name: Optional[str] = None,
    filepath: Optional[str] = None,
    line: int = 0,
    bookmark_file: Path = DEFAULT_BOOKMARK_FILE,
    out=None,
) -> int:
    """Execute a bookmark action. Returns exit code."""
    if out is None:
        out = sys.stdout

    if action == "set":
        if not name or not filepath:
            print("error: 'set' requires --name and --file", file=sys.stderr)
            return 1
        set_bookmark(name, filepath, line, bookmark_file)
        print(f"Bookmark {name!r} saved at {filepath}:{line}", file=out)
        return 0

    if action == "get":
        if not name:
            print("error: 'get' requires --name", file=sys.stderr)
            return 1
        bm = get_bookmark(name, bookmark_file)
        if bm is None:
            print(f"Bookmark {name!r} not found", file=sys.stderr)
            return 2
        print(f"{bm['file']}:{bm['line']}", file=out)
        return 0

    if action == "delete":
        if not name:
            print("error: 'delete' requires --name", file=sys.stderr)
            return 1
        removed = delete_bookmark(name, bookmark_file)
        if not removed:
            print(f"Bookmark {name!r} not found", file=sys.stderr)
            return 2
        print(f"Bookmark {name!r} deleted", file=out)
        return 0

    if action == "list":
        bms = list_bookmarks(bookmark_file)
        if not bms:
            print("No bookmarks saved.", file=out)
        else:
            for bname, info in sorted(bms.items()):
                print(f"{bname}: {info['file']}:{info['line']}", file=out)
        return 0

    print(f"error: unknown action {action!r}", file=sys.stderr)
    return 1
