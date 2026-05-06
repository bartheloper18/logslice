"""Tests for logslice.sample."""

from __future__ import annotations

import pytest

from logslice.sample import sample_lines


LINES = [f"line {i}\n" for i in range(1, 11)]  # line 1 .. line 10


# ---------------------------------------------------------------------------
# every-N mode
# ---------------------------------------------------------------------------

class TestEveryN:
    def test_every_1_keeps_all(self):
        assert list(sample_lines(LINES, every=1)) == LINES

    def test_every_2_keeps_even_indexed(self):
        result = list(sample_lines(LINES, every=2))
        assert result == ["line 2\n", "line 4\n", "line 6\n", "line 8\n", "line 10\n"]

    def test_every_5(self):
        result = list(sample_lines(LINES, every=5))
        assert result == ["line 5\n", "line 10\n"]

    def test_every_larger_than_input(self):
        result = list(sample_lines(["a\n", "b\n"], every=100))
        assert result == []

    def test_every_zero_raises(self):
        with pytest.raises(ValueError):
            list(sample_lines(LINES, every=0))

    def test_every_negative_raises(self):
        with pytest.raises(ValueError):
            list(sample_lines(LINES, every=-1))


# ---------------------------------------------------------------------------
# fraction mode
# ---------------------------------------------------------------------------

class TestFraction:
    def test_fraction_1_keeps_all(self):
        result = list(sample_lines(LINES, fraction=1.0, seed=0))
        assert result == LINES

    def test_fraction_0_raises(self):
        with pytest.raises(ValueError):
            list(sample_lines(LINES, fraction=0.0))

    def test_fraction_above_1_raises(self):
        with pytest.raises(ValueError):
            list(sample_lines(LINES, fraction=1.1))

    def test_fraction_is_reproducible_with_seed(self):
        r1 = list(sample_lines(LINES, fraction=0.5, seed=42))
        r2 = list(sample_lines(LINES, fraction=0.5, seed=42))
        assert r1 == r2

    def test_fraction_different_seeds_differ(self):
        r1 = list(sample_lines(LINES * 10, fraction=0.5, seed=1))
        r2 = list(sample_lines(LINES * 10, fraction=0.5, seed=99))
        assert r1 != r2


# ---------------------------------------------------------------------------
# mutual exclusion / missing mode
# ---------------------------------------------------------------------------

class TestValidation:
    def test_both_modes_raises(self):
        with pytest.raises(ValueError, match="not both"):
            list(sample_lines(LINES, every=2, fraction=0.5))

    def test_neither_mode_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            list(sample_lines(LINES))

    def test_empty_input_every(self):
        assert list(sample_lines([], every=2)) == []

    def test_empty_input_fraction(self):
        assert list(sample_lines([], fraction=0.5, seed=0)) == []
