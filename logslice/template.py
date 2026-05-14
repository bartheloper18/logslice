"""Template-based log line formatting.

Allows users to reshape log lines using a simple placeholder syntax:
  {field}  – replaced with the value of that field (JSON or KV)
  {_line}  – the original raw line
  {_lineno} – the current line number (1-based)

Example template: "{timestamp} [{level}] {message}"
"""

from __future__ import annotations

import re
import sys
from typing import IO, Iterable, Optional

from logslice.field import extract_json_fields, extract_kv_fields

_PLACEHOLDER = re.compile(r"\{(\w+)\}")


def render_template(template: str, fields: dict, line: str, lineno: int) -> str:
    """Substitute placeholders in *template* using *fields*.

    Special placeholders ``{_line}`` and ``{_lineno}`` are always available.
    Missing field names are left as-is.
    """
    ctx: dict = {"_line": line.rstrip("\n"), "_lineno": str(lineno)}
    ctx.update({k: str(v) for k, v in fields.items()})

    def _sub(m: re.Match) -> str:
        key = m.group(1)
        return ctx.get(key, m.group(0))

    result = _PLACEHOLDER.sub(_sub, template)
    return result


def _parse_fields(line: str) -> dict:
    """Try JSON then KV extraction; return empty dict on failure."""
    fields = extract_json_fields(line)
    if fields is not None:
        return fields
    fields = extract_kv_fields(line)
    return fields if fields is not None else {}


def template_lines(
    lines: Iterable[str],
    template: str,
    *,
    preserve_newline: bool = True,
) -> Iterable[str]:
    """Yield each line rendered through *template*."""
    for lineno, line in enumerate(lines, start=1):
        fields = _parse_fields(line)
        rendered = render_template(template, fields, line, lineno)
        if preserve_newline and not rendered.endswith("\n"):
            rendered += "\n"
        yield rendered


def template_file(
    path: str,
    template: str,
    out: IO[str] = sys.stdout,
    *,
    preserve_newline: bool = True,
) -> None:
    """Read *path*, apply *template* to every line, write to *out*."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for rendered in template_lines(fh, template, preserve_newline=preserve_newline):
            out.write(rendered)
