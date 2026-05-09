"""Tests for logslice.chunk."""

from __future__ import annotations

import pytest

from logslice.chunk import chunk_by_count, chunk_by_seconds, chunk_file


# ---------------------------------------------------------------------------
# chunk_by_count
# ---------------------------------------------------------------------------

class TestChunkByCount:
    def test_exact_multiple(self):
        lines = ["a\n", "b\n", "c\n", "d\n"]
        result = list(chunk_by_count(lines, 2))
        assert result == [["a\n", "b\n"], ["c\n", "d\n"]]

    def test_remainder_in_last_chunk(self):
        lines = ["a\n", "b\n", "c\n"]
        result = list(chunk_by_count(lines, 2))
        assert len(result) == 2
        assert result[-1] == ["c\n"]

    def test_size_larger_than_input(self):
        lines = ["x\n", "y\n"]
        result = list(chunk_by_count(lines, 100))
        assert result == [["x\n", "y\n"]]

    def test_empty_input(self):
        assert list(chunk_by_count([], 5)) == []

    def test_size_one(self):
        lines = ["a\n", "b\n", "c\n"]
        result = list(chunk_by_count(lines, 1))
        assert result == [["a\n"], ["b\n"], ["c\n"]]

    def test_invalid_size_raises(self):
        with pytest.raises(ValueError):
            list(chunk_by_count(["a\n"], 0))


# ---------------------------------------------------------------------------
# chunk_by_seconds
# ---------------------------------------------------------------------------

ISO = "2024-01-01T00:00:{:02d}Z line {}\n"


class TestChunkBySeconds:
    def _lines(self, offsets):
        return [ISO.format(s, i) for i, s in enumerate(offsets)]

    def test_single_window(self):
        lines = self._lines([0, 3, 5])
        result = list(chunk_by_seconds(lines, 10))
        assert len(result) == 1
        assert len(result[0]) == 3

    def test_splits_on_boundary(self):
        lines = self._lines([0, 5, 10, 15])
        result = list(chunk_by_seconds(lines, 10))
        assert len(result) == 2

    def test_no_timestamp_appended_to_current(self):
        lines = ["2024-01-01T00:00:00Z first\n", "no-timestamp\n",
                 "2024-01-01T00:00:20Z second\n"]
        result = list(chunk_by_seconds(lines, 10))
        assert "no-timestamp\n" in result[0]

    def test_empty_input(self):
        assert list(chunk_by_seconds([], 60)) == []

    def test_invalid_seconds_raises(self):
        with pytest.raises(ValueError):
            list(chunk_by_seconds(["a\n"], 0))


# ---------------------------------------------------------------------------
# chunk_file
# ---------------------------------------------------------------------------

def test_chunk_file_by_count(tmp_path):
    f = tmp_path / "log.txt"
    f.write_text("".join(f"line {i}\n" for i in range(6)))
    result = list(chunk_file(str(f), size=2))
    assert len(result) == 3


def test_chunk_file_no_args_raises(tmp_path):
    f = tmp_path / "log.txt"
    f.write_text("a\n")
    with pytest.raises(ValueError):
        list(chunk_file(str(f)))
