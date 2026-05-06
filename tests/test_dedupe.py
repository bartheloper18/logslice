"""Tests for logslice.dedupe."""

import os
import tempfile

import pytest

from logslice.dedupe import dedupe_lines, dedupe_file


# ---------------------------------------------------------------------------
# dedupe_lines – consecutive mode
# ---------------------------------------------------------------------------

class TestDedupeConsecutive:
    def _run(self, lines):
        return list(dedupe_lines(lines, consecutive_only=True))

    def test_no_duplicates_unchanged(self):
        lines = ["a\n", "b\n", "c\n"]
        assert self._run(lines) == lines

    def test_adjacent_duplicates_removed(self):
        lines = ["a\n", "a\n", "b\n", "b\n", "b\n", "c\n"]
        assert self._run(lines) == ["a\n", "b\n", "c\n"]

    def test_non_adjacent_duplicates_kept(self):
        lines = ["a\n", "b\n", "a\n"]
        assert self._run(lines) == ["a\n", "b\n", "a\n"]

    def test_empty_input(self):
        assert self._run([]) == []

    def test_single_line(self):
        assert self._run(["only\n"]) == ["only\n"]

    def test_preserves_trailing_newline(self):
        result = self._run(["hello\n", "hello\n"])
        assert result == ["hello\n"]

    def test_lines_without_newline(self):
        lines = ["x", "x", "y"]
        assert self._run(lines) == ["x", "y"]


# ---------------------------------------------------------------------------
# dedupe_lines – windowed (global) mode
# ---------------------------------------------------------------------------

class TestDedupeWindowed:
    def _run(self, lines, max_cache=1024):
        return list(dedupe_lines(lines, consecutive_only=False, max_cache=max_cache))

    def test_no_duplicates_unchanged(self):
        lines = ["a\n", "b\n", "c\n"]
        assert self._run(lines) == lines

    def test_non_adjacent_duplicates_removed(self):
        lines = ["a\n", "b\n", "a\n", "c\n", "b\n"]
        assert self._run(lines) == ["a\n", "b\n", "c\n"]

    def test_all_same(self):
        lines = ["dup\n"] * 10
        assert self._run(lines) == ["dup\n"]

    def test_cache_eviction_allows_reappearance(self):
        # cache size 2: after eviction, "a" can reappear
        lines = ["a\n", "b\n", "c\n", "a\n"]
        result = self._run(lines, max_cache=2)
        # "a" evicted when "c" inserted; second "a" should pass through
        assert result == ["a\n", "b\n", "c\n", "a\n"]

    def test_empty_input(self):
        assert self._run([]) == []


# ---------------------------------------------------------------------------
# dedupe_file
# ---------------------------------------------------------------------------

class TestDedupeFile:
    def _make_file(self, lines):
        fd, path = tempfile.mkstemp(suffix=".log")
        with os.fdopen(fd, "w") as fh:
            fh.writelines(lines)
        return path

    def test_file_deduplication(self):
        path = self._make_file(["INFO start\n", "INFO start\n", "ERROR boom\n"])
        try:
            result = list(dedupe_file(path))
            assert result == ["INFO start\n", "ERROR boom\n"]
        finally:
            os.unlink(path)

    def test_consecutive_only_flag(self):
        path = self._make_file(["a\n", "b\n", "a\n"])
        try:
            result = list(dedupe_file(path, consecutive_only=True))
            assert result == ["a\n", "b\n", "a\n"]
        finally:
            os.unlink(path)
