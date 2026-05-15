"""Tests for logslice.limit and logslice.limit_cmd."""

from __future__ import annotations

import argparse
import io
import os
import tempfile

import pytest

from logslice.limit import limit_lines, limit_file
from logslice.limit_cmd import build_limit_parser, run_limit, _parse_size


# ---------------------------------------------------------------------------
# _parse_size
# ---------------------------------------------------------------------------

def test_parse_size_plain_int():
    assert _parse_size("1024") == 1024

def test_parse_size_k_suffix():
    assert _parse_size("2k") == 2048

def test_parse_size_m_suffix():
    assert _parse_size("1m") == 1024 ** 2

def test_parse_size_uppercase():
    assert _parse_size("4K") == 4096


# ---------------------------------------------------------------------------
# limit_lines
# ---------------------------------------------------------------------------

class TestLimitLines:
    def _run(self, lines, max_bytes, truncate=False):
        return list(limit_lines(lines, max_bytes, truncate=truncate))

    def test_all_lines_fit(self):
        lines = ["hello\n", "world\n"]
        assert self._run(lines, 1000) == lines

    def test_zero_budget_returns_nothing(self):
        assert self._run(["hello\n"], 0) == []

    def test_negative_budget_returns_nothing(self):
        assert self._run(["hello\n"], -5) == []

    def test_exact_budget_keeps_line(self):
        line = "hello\n"  # 6 bytes
        assert self._run([line], 6) == [line]

    def test_budget_exhausted_drops_excess(self):
        lines = ["aaa\n", "bbb\n", "ccc\n"]  # 4 bytes each
        result = self._run(lines, 8)
        assert result == ["aaa\n", "bbb\n"]

    def test_single_line_exceeds_budget_dropped(self):
        result = self._run(["hello world\n"], 5)
        assert result == []

    def test_single_line_exceeds_budget_truncated(self):
        result = self._run(["hello world\n"], 5, truncate=True)
        assert len(result) == 1
        assert result[0].encode() == b"hello"

    def test_truncate_mid_stream(self):
        lines = ["aaa\n", "bbbbbbb\n"]
        result = self._run(lines, 6, truncate=True)
        assert result[0] == "aaa\n"
        assert result[1].encode() == b"bb"  # 6 - 4 = 2 bytes remaining

    def test_stops_after_budget_hit(self):
        lines = ["aa\n"] * 10  # 3 bytes each
        result = self._run(lines, 9)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# limit_file
# ---------------------------------------------------------------------------

def test_limit_file_writes_output():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write("line one\n")
        f.write("line two\n")
        f.write("line three\n")
        fname = f.name
    try:
        out = io.StringIO()
        count = limit_file(fname, 18, out)
        assert count == 2
        assert out.getvalue() == "line one\nline two\n"
    finally:
        os.unlink(fname)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    defaults = {"size": "1k", "file": None, "truncate": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(args, stdin_lines=None):
    out = io.StringIO()
    if stdin_lines is not None:
        import unittest.mock as mock
        import sys
        with mock.patch("sys.stdin", io.StringIO("".join(stdin_lines))):
            rc = run_limit(args, out=out)
    else:
        rc = run_limit(args, out=out)
    return rc, out.getvalue()


def test_build_limit_parser_returns_parser():
    p = build_limit_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_invalid_size_returns_error():
    args = _ns(size="notasize")
    out = io.StringIO()
    rc = run_limit(args, out=out)
    assert rc == 1


def test_stdin_respected():
    args = _ns(size="10")
    rc, output = _run(args, stdin_lines=["hello\n", "world\n"])
    assert rc == 0
    assert "hello" in output
