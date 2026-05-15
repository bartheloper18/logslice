"""Tests for logslice.head."""

from __future__ import annotations

import io
import os
import tempfile

import pytest

from logslice.head import head_lines, head_file


# ---------------------------------------------------------------------------
# head_lines
# ---------------------------------------------------------------------------

class TestHeadLines:
    def _run(self, lines, n):
        return list(head_lines(lines, n=n))

    def test_returns_first_n(self):
        lines = ["a\n", "b\n", "c\n", "d\n", "e\n"]
        assert self._run(lines, 3) == ["a\n", "b\n", "c\n"]

    def test_n_larger_than_input_returns_all(self):
        lines = ["x\n", "y\n"]
        assert self._run(lines, 100) == ["x\n", "y\n"]

    def test_n_zero_returns_empty(self):
        assert self._run(["a\n", "b\n"], 0) == []

    def test_n_negative_returns_empty(self):
        assert self._run(["a\n", "b\n"], -5) == []

    def test_empty_input_returns_empty(self):
        assert self._run([], 10) == []

    def test_n_equals_length(self):
        lines = ["1\n", "2\n", "3\n"]
        assert self._run(lines, 3) == lines

    def test_generator_input(self):
        def gen():
            for i in range(5):
                yield f"line{i}\n"
        result = self._run(gen(), 2)
        assert result == ["line0\n", "line1\n"]

    def test_default_n_is_10(self):
        lines = [f"{i}\n" for i in range(20)]
        result = list(head_lines(lines))
        assert len(result) == 10
        assert result[0] == "0\n"
        assert result[-1] == "9\n"


# ---------------------------------------------------------------------------
# head_file
# ---------------------------------------------------------------------------

class TestHeadFile:
    def _make_file(self, lines):
        fd, path = tempfile.mkstemp(suffix=".log")
        with os.fdopen(fd, "w") as fh:
            fh.writelines(lines)
        return path

    def test_returns_first_n_lines(self):
        path = self._make_file([f"line{i}\n" for i in range(20)])
        buf = io.StringIO()
        count = head_file(path, n=5, out=buf)
        assert count == 5
        assert buf.getvalue() == "".join(f"line{i}\n" for i in range(5))

    def test_n_larger_than_file(self):
        path = self._make_file(["a\n", "b\n"])
        buf = io.StringIO()
        count = head_file(path, n=50, out=buf)
        assert count == 2
        assert buf.getvalue() == "a\nb\n"

    def test_n_zero_writes_nothing(self):
        path = self._make_file(["a\n", "b\n"])
        buf = io.StringIO()
        count = head_file(path, n=0, out=buf)
        assert count == 0
        assert buf.getvalue() == ""

    def test_lines_without_newline_get_newline(self):
        fd, path = tempfile.mkstemp(suffix=".log")
        with os.fdopen(fd, "w") as fh:
            fh.write("no-newline")
        buf = io.StringIO()
        head_file(path, n=1, out=buf)
        assert buf.getvalue() == "no-newline\n"
