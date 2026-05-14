"""Sort log lines by timestamp or field value."""

from __future__ import annotations

import io
from typing import Iterable, Iterator, Optional

from logslice.parser import extract_timestamp
from logslice.field import extract_json_fields, extract_kv_fields


def _sort_key_timestamp(line: str):
    """Return a sort key based on the extracted timestamp, or a max sentinel."""
    ts = extract_timestamp(line)
    if ts is None:
        return (1, line)
    return (0, ts)


def _sort_key_field(line: str, field: str):
    """Return a sort key based on a named field value."""
    fields = extract_json_fields(line) or extract_kv_fields(line) or {}
    value = fields.get(field, "")
    return value


def sort_lines(
    lines: Iterable[str],
    *,
    key: str = "timestamp",
    reverse: bool = False,
    stable: bool = True,
) -> list[str]:
    """Sort *lines* by *key*.

    Parameters
    ----------
    lines:
        Iterable of raw log lines.
    key:
        ``"timestamp"`` to sort by detected timestamp, or any field name to
        sort by that field's value (JSON / key=value pairs supported).
    reverse:
        If ``True``, sort descending.
    stable:
        Python's sort is always stable; this flag is accepted for API
        consistency and has no effect.
    """
    items = list(lines)
    if key == "timestamp":
        items.sort(key=_sort_key_timestamp, reverse=reverse)
    else:
        items.sort(key=lambda ln: _sort_key_field(ln, key), reverse=reverse)
    return items


def sort_file(
    path: str,
    out: io.TextIOBase,
    *,
    key: str = "timestamp",
    reverse: bool = False,
) -> None:
    """Read *path*, sort all lines, and write results to *out*."""
    with open(path, "r", errors="replace") as fh:
        lines = fh.readlines()
    for line in sort_lines(lines, key=key, reverse=reverse):
        out.write(line)
