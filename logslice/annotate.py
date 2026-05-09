"""Annotate log lines with derived metadata (line number, elapsed time, delta)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional

from logslice.parser import extract_timestamp


@dataclass
class AnnotatedLine:
    lineno: int
    text: str
    elapsed_ms: Optional[float]  # ms since first timestamped line
    delta_ms: Optional[float]    # ms since previous timestamped line


def annotate_lines(
    lines: Iterable[str],
    *,
    show_lineno: bool = True,
    show_elapsed: bool = False,
    show_delta: bool = False,
) -> Iterator[AnnotatedLine]:
    """Yield AnnotatedLine objects for each input line."""
    first_ts = None
    prev_ts = None

    for lineno, text in enumerate(lines, start=1):
        ts = extract_timestamp(text)
        elapsed_ms: Optional[float] = None
        delta_ms: Optional[float] = None

        if ts is not None:
            if first_ts is None:
                first_ts = ts
            if show_elapsed and first_ts is not None:
                elapsed_ms = (ts - first_ts).total_seconds() * 1000
            if show_delta and prev_ts is not None:
                delta_ms = (ts - prev_ts).total_seconds() * 1000
            prev_ts = ts

        yield AnnotatedLine(
            lineno=lineno,
            text=text,
            elapsed_ms=elapsed_ms,
            delta_ms=delta_ms,
        )


def format_annotated(ann: AnnotatedLine, *, show_lineno: bool, show_elapsed: bool, show_delta: bool) -> str:
    """Format an AnnotatedLine into a prefixed string."""
    parts: list[str] = []
    if show_lineno:
        parts.append(f"[{ann.lineno:>6}]")
    if show_elapsed:
        val = f"{ann.elapsed_ms:.1f}" if ann.elapsed_ms is not None else "      -"
        parts.append(f"[+{val:>10}ms]")
    if show_delta:
        val = f"{ann.delta_ms:.1f}" if ann.delta_ms is not None else "      -"
        parts.append(f"[d{val:>10}ms]")
    prefix = " ".join(parts)
    text = ann.text.rstrip("\n")
    return f"{prefix} {text}\n" if prefix else f"{text}\n"
