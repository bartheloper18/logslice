"""Split log lines into separate files based on a field value or pattern."""

from __future__ import annotations

import os
import re
from typing import Dict, IO, Iterable, Optional

from logslice.field import extract_json_fields, extract_kv_fields


def _safe_filename(value: str) -> str:
    """Sanitise a field value so it can be used as part of a filename."""
    value = value.strip()
    value = re.sub(r"[^\w.\-]", "_", value)
    return value or "unknown"


def _get_key(line: str, field: Optional[str], pattern: Optional[re.Pattern]) -> str:
    """Return the bucket key for *line*."""
    if field:
        fields = extract_json_fields(line) or extract_kv_fields(line) or {}
        return _safe_filename(str(fields.get(field, "unknown")))
    if pattern:
        m = pattern.search(line)
        if m:
            groups = m.groupdict()
            if groups:
                return _safe_filename(next(iter(groups.values())))
            if m.lastindex:
                return _safe_filename(m.group(1))
            return _safe_filename(m.group(0))
    return "default"


def split_lines(
    lines: Iterable[str],
    output_dir: str,
    prefix: str = "split",
    field: Optional[str] = None,
    pattern: Optional[re.Pattern] = None,
    suffix: str = ".log",
) -> Dict[str, int]:
    """Write *lines* into per-bucket files under *output_dir*.

    Returns a mapping of ``bucket_key -> line_count``.
    """
    os.makedirs(output_dir, exist_ok=True)
    handles: Dict[str, IO[str]] = {}
    counts: Dict[str, int] = {}
    try:
        for line in lines:
            key = _get_key(line, field, pattern)
            if key not in handles:
                path = os.path.join(output_dir, f"{prefix}_{key}{suffix}")
                handles[key] = open(path, "a", encoding="utf-8")
                counts[key] = 0
            handles[key].write(line if line.endswith("\n") else line + "\n")
            counts[key] += 1
    finally:
        for fh in handles.values():
            fh.close()
    return counts


def split_file(
    path: str,
    output_dir: str,
    prefix: str = "split",
    field: Optional[str] = None,
    pattern: Optional[re.Pattern] = None,
    suffix: str = ".log",
) -> Dict[str, int]:
    """Convenience wrapper that opens *path* and delegates to :func:`split_lines`."""
    with open(path, encoding="utf-8") as fh:
        return split_lines(
            fh, output_dir, prefix=prefix, field=field, pattern=pattern, suffix=suffix
        )
