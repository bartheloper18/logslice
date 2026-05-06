"""Log line sampling: return every Nth line or a random fraction."""

from __future__ import annotations

import random
from typing import Iterable, Iterator, TextIO


def sample_lines(
    lines: Iterable[str],
    *,
    every: int = 0,
    fraction: float = 0.0,
    seed: int | None = None,
) -> Iterator[str]:
    """Yield a subset of *lines*.

    Exactly one of *every* or *fraction* must be non-zero.

    Args:
        lines:    Source iterable of log lines.
        every:    Keep every Nth line (1-based counter; ``every=1`` keeps all).
        fraction: Keep each line with this probability (0 < fraction <= 1.0).
        seed:     Optional RNG seed for reproducible fraction sampling.

    Raises:
        ValueError: If neither or both modes are specified, or values are invalid.
    """
    if every and fraction:
        raise ValueError("Specify either 'every' or 'fraction', not both.")
    if not every and not fraction:
        raise ValueError("Specify at least one of 'every' or 'fraction'.")
    if every and every < 1:
        raise ValueError("'every' must be >= 1.")
    if fraction and not (0.0 < fraction <= 1.0):
        raise ValueError("'fraction' must be in the range (0, 1].")

    if every:
        for idx, line in enumerate(lines, start=1):
            if idx % every == 0:
                yield line
    else:
        rng = random.Random(seed)
        for line in lines:
            if rng.random() < fraction:
                yield line


def sample_file(
    fh: TextIO,
    *,
    every: int = 0,
    fraction: float = 0.0,
    seed: int | None = None,
) -> Iterator[str]:
    """Convenience wrapper around :func:`sample_lines` for open file handles."""
    yield from sample_lines(fh, every=every, fraction=fraction, seed=seed)
