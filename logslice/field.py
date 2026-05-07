"""Field extraction for structured log formats (key=value, JSON)."""

import json
import re
from typing import Any, Dict, List, Optional

_KV_RE = re.compile(r'([\w.\-]+)=(?:"([^"]*)"|([^\s,]*))')


def extract_json_fields(line: str) -> Optional[Dict[str, Any]]:
    """Return parsed JSON object if *line* is valid JSON, else None."""
    stripped = line.strip()
    if not stripped.startswith("{"):
        return None
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    return None


def extract_kv_fields(line: str) -> Dict[str, str]:
    """Extract key=value pairs from *line* into a dict.

    Supports quoted values: key="hello world" and bare values: key=foo.
    """
    result: Dict[str, str] = {}
    for m in _KV_RE.finditer(line):
        key = m.group(1)
        value = m.group(2) if m.group(2) is not None else m.group(3)
        result[key] = value
    return result


def get_field(
    line: str, field: str, *, prefer_json: bool = True
) -> Optional[str]:
    """Return the value of *field* extracted from *line* or None."""
    if prefer_json:
        obj = extract_json_fields(line)
        if obj is not None:
            val = obj.get(field)
            return str(val) if val is not None else None
    kv = extract_kv_fields(line)
    return kv.get(field)


def filter_by_field(
    lines: List[str], field: str, value: str, *, ignore_case: bool = False
) -> List[str]:
    """Return lines where *field* equals *value*."""
    if ignore_case:
        value = value.lower()

    out: List[str] = []
    for line in lines:
        extracted = get_field(line, field)
        if extracted is None:
            continue
        cmp = extracted.lower() if ignore_case else extracted
        if cmp == value:
            out.append(line)
    return out
