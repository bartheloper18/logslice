"""Tests for logslice.truncate."""

import io
import os
import tempfile

import pytest

from logslice.truncate import (
    DEFAULT_MAX_WIDTH,
    truncate_file,
    truncate_line,
    truncate_lines,
)


class TestTruncateLine:
    def test_short_line_unchanged(self):
        assert truncate_line("hello", max_width=80) == "hello"

    def test_exact_length_unchanged(self):
        line = "x" * 20
        assert truncate_line(line, max_width=20) == line

    def test_long_line_truncated(self):
        line = "a" * 50
        result = truncate_line(line, max_width=10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_newline_preserved_when_short(self):
        assert truncate_line("hello\n", max_width=80) == "hello\n"

    def test_newline_preserved_after_truncation(self):
        line = "b" * 50 + "\n"
        result = truncate_line(line, max_width=10)
        assert result.endswith("...\n")
        # content length (without newline) == max_width
        assert len(result.rstrip("\n")) == 10

    def test_custom_ellipsis(self):
        line = "z" * 30
        result = truncate_line(line, max_width=10, ellipsis=">")
        assert result == "z" * 9 + ">"

    def test_invalid_max_width_raises(self):
        with pytest.raises(ValueError):
            truncate_line("hello", max_width=0)

    def test_ellipsis_longer_than_max_width(self):
        # cut becomes 0; result is just the ellipsis truncated
        result = truncate_line("hello world", max_width=2, ellipsis="...")
        assert len(result) == 2


class TestTruncateLines:
    def test_all_short_lines_unchanged(self):
        lines = ["foo\n", "bar\n", "baz\n"]
        result = list(truncate_lines(lines, max_width=80))
        assert result == lines

    def test_long_lines_truncated(self):
        lines = ["a" * 200 + "\n", "short\n"]
        result = list(truncate_lines(lines, max_width=20))
        assert len(result[0].rstrip("\n")) == 20
        assert result[1] == "short\n"

    def test_generator_input(self):
        def gen():
            yield "x" * 10 + "\n"
            yield "y" * 10 + "\n"

        result = list(truncate_lines(gen(), max_width=5))
        assert all(len(r.rstrip("\n")) == 5 for r in result)


class TestTruncateFile:
    def _make_file(self, lines):
        tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log")
        tmp.writelines(lines)
        tmp.close()
        return tmp.name

    def teardown_method(self, _method):
        # nothing persistent to clean up beyond individual tests
        pass

    def test_writes_truncated_output(self):
        path = self._make_file(["a" * 100 + "\n", "short\n"])
        try:
            out = io.StringIO()
            truncate_file(path, max_width=20, out=out)
            lines = out.getvalue().splitlines()
            assert len(lines[0]) == 20
            assert lines[1] == "short"
        finally:
            os.unlink(path)

    def test_default_max_width_applied(self):
        long_line = "L" * (DEFAULT_MAX_WIDTH + 50) + "\n"
        path = self._make_file([long_line])
        try:
            out = io.StringIO()
            truncate_file(path, out=out)
            result = out.getvalue().rstrip("\n")
            assert len(result) == DEFAULT_MAX_WIDTH
        finally:
            os.unlink(path)
