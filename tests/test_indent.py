"""Tests for logslice.indent."""

from __future__ import annotations

import io
import os
import tempfile

import pytest

from logslice.indent import indent_line, outdent_line, indent_lines, indent_file


# ---------------------------------------------------------------------------
# indent_line
# ---------------------------------------------------------------------------

class TestIndentLine:
    def test_adds_default_prefix(self):
        assert indent_line("hello", "    ") == "    hello"

    def test_preserves_trailing_newline(self):
        assert indent_line("hello\n", "  ") == "  hello\n"

    def test_empty_prefix_unchanged(self):
        assert indent_line("hello\n", "") == "hello\n"

    def test_custom_string_prefix(self):
        assert indent_line("msg", ">> ") == ">> msg"

    def test_empty_line_gets_prefix(self):
        assert indent_line("", "  ") == "  "

    def test_empty_line_with_newline(self):
        assert indent_line("\n", "  ") == "  \n"


# ---------------------------------------------------------------------------
# outdent_line
# ---------------------------------------------------------------------------

class TestOutdentLine:
    def test_removes_matching_prefix(self):
        assert outdent_line("    hello", "    ") == "hello"

    def test_preserves_newline_after_removal(self):
        assert outdent_line("  hi\n", "  ") == "hi\n"

    def test_no_match_returns_original(self):
        assert outdent_line("hello", "    ") == "hello"

    def test_partial_prefix_not_removed(self):
        assert outdent_line("  hello", "    ") == "  hello"

    def test_empty_prefix_unchanged(self):
        assert outdent_line("hello", "") == "hello"


# ---------------------------------------------------------------------------
# indent_lines
# ---------------------------------------------------------------------------

def test_indent_lines_multiple():
    lines = ["one\n", "two\n", "three\n"]
    result = list(indent_lines(lines, "  "))
    assert result == ["  one\n", "  two\n", "  three\n"]


def test_outdent_lines_flag():
    lines = ["  one\n", "  two\n"]
    result = list(indent_lines(lines, "  ", outdent=True))
    assert result == ["one\n", "two\n"]


def test_indent_lines_empty_input():
    assert list(indent_lines([], "  ")) == []


# ---------------------------------------------------------------------------
# indent_file
# ---------------------------------------------------------------------------

def test_indent_file_writes_to_out():
    content = "line one\nline two\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(content)
        fname = f.name
    try:
        buf = io.StringIO()
        indent_file(fname, ">> ", out=buf)
        assert buf.getvalue() == ">> line one\n>> line two\n"
    finally:
        os.unlink(fname)


def test_outdent_file_writes_to_out():
    content = "  a\n  b\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(content)
        fname = f.name
    try:
        buf = io.StringIO()
        indent_file(fname, "  ", outdent=True, out=buf)
        assert buf.getvalue() == "a\nb\n"
    finally:
        os.unlink(fname)
