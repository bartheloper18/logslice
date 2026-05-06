"""Merge and interleave multiple log files sorted by timestamp."""

from __future__ import annotations

import heapq
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Tuple

from logslice.parser import extract_timestamp


def _iter_timestamped(path: str, tag: bool = False) -> Iterator[Tuple]:
    """Yield (timestamp, line_no, line, source) tuples from a file.

    Lines without a parseable timestamp are assigned the timestamp of the
    most-recently seen timestamped line so they stay grouped with their
    parent entry.
    """
    last_ts = None
    source = Path(path).name
    try:
        with open(path, "r", errors="replace") as fh:
            for lineno, raw in enumerate(fh):
                line = raw.rstrip("\n")
                ts = extract_timestamp(line)
                if ts is not None:
                    last_ts = ts
                effective_ts = last_ts
                yield (effective_ts, lineno, line, source)
    except OSError as exc:
        raise OSError(f"Cannot open '{path}': {exc}") from exc


def merge_files(
    paths: List[str],
    tag: bool = False,
    skip_unparsed: bool = False,
) -> Iterator[str]:
    """Merge log lines from multiple *paths* in chronological order.

    Args:
        paths: List of file paths to merge.
        tag:   Prefix each output line with the source filename.
        skip_unparsed: Drop lines that have no resolvable timestamp.

    Yields:
        Merged log lines (without trailing newline).
    """
    iterators = [_iter_timestamped(p, tag=tag) for p in paths]

    # heapq.merge requires comparable items; None timestamps sort first.
    # We convert None -> "" so strings remain comparable.
    def _key(item: Tuple) -> Tuple:
        ts, lineno, line, source = item
        return (ts or "", lineno, source)

    for ts, lineno, line, source in heapq.merge(*iterators, key=_key):
        if skip_unparsed and ts is None:
            continue
        if tag:
            yield f"{source}: {line}"
        else:
            yield line


def merge_to_file(
    paths: List[str],
    output_path: str,
    tag: bool = False,
    skip_unparsed: bool = False,
) -> int:
    """Write merged output to *output_path*; return number of lines written."""
    count = 0
    with open(output_path, "w") as out:
        for line in merge_files(paths, tag=tag, skip_unparsed=skip_unparsed):
            out.write(line + "\n")
            count += 1
    return count
