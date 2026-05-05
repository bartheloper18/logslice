"""Context-line support: show lines before/after each match (like grep -A/-B/-C)."""

from collections import deque
from typing import Iterable, Iterator, List, NamedTuple, Pattern


SEPARATOR = "--"


class ContextLine(NamedTuple):
    """A log line annotated with match and context metadata."""

    lineno: int
    text: str
    is_match: bool


def context_grep(
    lines: Iterable[str],
    pattern: Pattern[str],
    before: int = 0,
    after: int = 0,
    invert: bool = False,
) -> Iterator[ContextLine]:
    """Yield ContextLine objects for matching lines and their context.

    Args:
        lines: Iterable of log lines.
        pattern: Compiled regex pattern.
        before: Number of lines to include before each match.
        after: Number of lines to include after each match.
        invert: Invert the match logic.

    Yields:
        ContextLine for each line that should be output.
    """
    buffer: deque = deque(maxlen=max(before, 1))
    pending_after: int = 0
    emitted: set = set()

    all_lines: List[str] = list(lines)

    for idx, line in enumerate(all_lines):
        matched = (pattern.search(line) is not None) ^ invert

        if matched:
            # Emit buffered before-context
            start = max(0, idx - before)
            for bi in range(start, idx):
                if bi not in emitted:
                    emitted.add(bi)
                    yield ContextLine(bi + 1, all_lines[bi], False)
            # Emit the match itself
            emitted.add(idx)
            yield ContextLine(idx + 1, line, True)
            pending_after = after
        elif pending_after > 0:
            if idx not in emitted:
                emitted.add(idx)
                yield ContextLine(idx + 1, line, False)
            pending_after -= 1

        buffer.append(line)


def format_context_output(
    context_lines: Iterable[ContextLine],
    show_lineno: bool = False,
    separator: str = SEPARATOR,
) -> Iterator[str]:
    """Format ContextLine objects into printable strings.

    Inserts separator lines between non-contiguous groups.

    Args:
        context_lines: Iterable of ContextLine objects.
        show_lineno: Prefix each line with its line number.
        separator: String used to separate context groups.

    Yields:
        Formatted strings ready for output.
    """
    prev_lineno: int = -1
    for cl in context_lines:
        if prev_lineno != -1 and cl.lineno > prev_lineno + 1:
            yield separator
        prefix = f"{cl.lineno}:" if show_lineno else ""
        yield f"{prefix}{cl.text.rstrip()}"
        prev_lineno = cl.lineno
