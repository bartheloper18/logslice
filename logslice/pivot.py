"""pivot.py – transpose log fields into a columnar summary table.

For each unique value of a chosen key field, count occurrences and
optionally aggregate a numeric value field (sum / mean).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Optional

from logslice.field import extract_json_fields, extract_kv_fields


def _parse_fields(line: str) -> Optional[dict]:
    """Return a field dict from JSON or key=value line, else None."""
    fields = extract_json_fields(line)
    if fields is not None:
        return fields
    fields = extract_kv_fields(line)
    return fields if fields else None


def pivot_lines(
    lines: Iterable[str],
    key: str,
    value: Optional[str] = None,
    agg: str = "count",
) -> dict[str, dict]:
    """Aggregate *lines* grouped by the *key* field.

    Parameters
    ----------
    lines:  iterable of raw log lines
    key:    field name to group by
    value:  optional numeric field to aggregate (sum / mean)
    agg:    'count', 'sum', or 'mean' (mean implies a value field)

    Returns a dict mapping each key-value -> {count, sum, mean}.
    """
    counts: dict[str, int] = defaultdict(int)
    totals: dict[str, float] = defaultdict(float)

    for line in lines:
        fields = _parse_fields(line.rstrip("\n"))
        if fields is None:
            continue
        k = fields.get(key)
        if k is None:
            continue
        k = str(k)
        counts[k] += 1
        if value is not None:
            try:
                totals[k] += float(fields[value])
            except (KeyError, TypeError, ValueError):
                pass

    result: dict[str, dict] = {}
    for k, cnt in sorted(counts.items()):
        entry: dict = {"count": cnt}
        if value is not None:
            s = totals[k]
            entry["sum"] = s
            entry["mean"] = s / cnt if cnt else 0.0
        result[k] = entry
    return result


def format_pivot(data: dict[str, dict], value: Optional[str] = None) -> str:
    """Render the pivot table as a fixed-width string."""
    if not data:
        return "(no data)\n"
    has_value = value is not None
    header = f"{'KEY':<30}  {'COUNT':>8}"
    if has_value:
        header += f"  {'SUM':>12}  {'MEAN':>12}"
    rows = [header, "-" * len(header)]
    for k, entry in data.items():
        row = f"{k:<30}  {entry['count']:>8}"
        if has_value:
            row += f"  {entry['sum']:>12.3f}  {entry['mean']:>12.3f}"
        rows.append(row)
    return "\n".join(rows) + "\n"
