"""diff.py – compare two log files and surface lines unique to each."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional

from logslice.parser import extract_timestamp


@dataclass
class DiffLine:
    side: str        # 'left', 'right', or 'both'
    lineno_left: Optional[int]
    lineno_right: Optional[int]
    text: str


def _normalise(line: str) -> str:
    """Strip trailing whitespace/newline for comparison."""
    return line.rstrip()


def diff_lines(
    left: Iterable[str],
    right: Iterable[str],
    *,
    ignore_timestamps: bool = False,
) -> Iterator[DiffLine]:
    """Yield DiffLine entries showing which lines appear in left, right, or both.

    When *ignore_timestamps* is True the timestamp portion of each line is
    stripped before comparison so that identical messages with different
    timestamps are treated as equal.
    """
    left_lines: List[str] = [_normalise(l) for l in left]
    right_lines: List[str] = [_normalise(l) for l in right]

    def key(text: str) -> str:
        if ignore_timestamps:
            ts = extract_timestamp(text)
            if ts is not None:
                return text[text.index(ts[1]) + len(ts[1]):].lstrip()
        return text

    right_keys = {key(t): i for i, t in enumerate(right_lines)}
    left_keys = {key(t): i for i, t in enumerate(left_lines)}

    emitted_right: set = set()

    for li, lt in enumerate(left_lines):
        lk = key(lt)
        if lk in right_keys:
            ri = right_keys[lk]
            emitted_right.add(ri)
            yield DiffLine(side="both", lineno_left=li + 1, lineno_right=ri + 1, text=lt)
        else:
            yield DiffLine(side="left", lineno_left=li + 1, lineno_right=None, text=lt)

    for ri, rt in enumerate(right_lines):
        if ri not in emitted_right:
            yield DiffLine(side="right", lineno_left=None, lineno_right=ri + 1, text=rt)


def format_diff(
    entries: Iterable[DiffLine],
    *,
    color: bool = False,
    only: Optional[str] = None,
) -> Iterator[str]:
    """Format DiffLine entries as human-readable strings.

    *only* can be 'left', 'right', or 'both' to restrict output.
    """
    LEFT_COLOR = "\033[31m"   # red
    RIGHT_COLOR = "\033[32m"  # green
    BOTH_COLOR = "\033[0m"    # reset
    RESET = "\033[0m"

    prefix = {"left": "< ", "right": "> ", "both": "  "}

    for entry in entries:
        if only and entry.side != only:
            continue
        pfx = prefix[entry.side]
        line = f"{pfx}{entry.text}"
        if color:
            if entry.side == "left":
                line = f"{LEFT_COLOR}{line}{RESET}"
            elif entry.side == "right":
                line = f"{RIGHT_COLOR}{line}{RESET}"
            else:
                line = f"{BOTH_COLOR}{line}{RESET}"
        yield line
