"""Relevance scoring for log lines based on keyword weights."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional, TextIO


@dataclass
class ScoredLine:
    lineno: int
    text: str
    score: float
    matched: List[str] = field(default_factory=list)


def compile_weights(weights: Dict[str, float]) -> List[tuple]:
    """Return a list of (compiled_pattern, weight) tuples."""
    return [(re.compile(pattern, re.IGNORECASE), w) for pattern, w in weights.items()]


def score_line(text: str, compiled: List[tuple]) -> tuple[float, List[str]]:
    """Return (total_score, matched_patterns) for a single line."""
    total = 0.0
    matched: List[str] = []
    for pattern, weight in compiled:
        if pattern.search(text):
            total += weight
            matched.append(pattern.pattern)
    return total, matched


def score_lines(
    lines: Iterable[str],
    weights: Dict[str, float],
    threshold: float = 0.0,
    top_n: Optional[int] = None,
) -> List[ScoredLine]:
    """Score each line and return those meeting *threshold*, sorted by score desc."""
    compiled = compile_weights(weights)
    results: List[ScoredLine] = []
    for lineno, text in enumerate(lines, start=1):
        s, matched = score_line(text, compiled)
        if s >= threshold:
            results.append(ScoredLine(lineno=lineno, text=text, score=s, matched=matched))
    results.sort(key=lambda sl: sl.score, reverse=True)
    if top_n is not None:
        results = results[:top_n]
    return results


def format_scored(sl: ScoredLine, show_score: bool = True, show_lineno: bool = True) -> str:
    """Format a ScoredLine for display."""
    parts: List[str] = []
    if show_lineno:
        parts.append(f"{sl.lineno:>6}")
    if show_score:
        parts.append(f"{sl.score:>7.2f}")
    parts.append(sl.text.rstrip("\n"))
    return "  ".join(parts)


def score_file(
    fh: TextIO,
    weights: Dict[str, float],
    threshold: float = 0.0,
    top_n: Optional[int] = None,
) -> List[ScoredLine]:
    """Score lines from an open file handle."""
    return score_lines(fh, weights, threshold=threshold, top_n=top_n)
