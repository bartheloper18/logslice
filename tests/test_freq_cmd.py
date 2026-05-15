"""Tests for logslice.freq_cmd."""
from __future__ import annotations

import io
import argparse

import pytest

from logslice.freq_cmd import build_freq_parser, run_freq


def _ns(**kwargs) -> argparse.Namespace:
    defaults = dict(files=[], field=None, top=None, no_header=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(lines: list[str], **kwargs) -> str:
    """Run freq against *lines* (via a temp file) and return captured output."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as fh:
        fh.writelines(lines)
        name = fh.name
    try:
        out = io.StringIO()
        args = _ns(files=[name], **kwargs)
        run_freq(args, out=out)
        return out.getvalue()
    finally:
        os.unlink(name)


class TestBuildFreqParser:
    def test_returns_parser(self):
        p = build_freq_parser()
        assert isinstance(p, argparse.ArgumentParser)

    def test_defaults(self):
        p = build_freq_parser()
        args = p.parse_args([])
        assert args.field is None
        assert args.top is None
        assert args.no_header is False

    def test_field_short_flag(self):
        p = build_freq_parser()
        args = p.parse_args(["-f", "level"])
        assert args.field == "level"

    def test_top_flag(self):
        p = build_freq_parser()
        args = p.parse_args(["--top", "5"])
        assert args.top == 5


class TestRunFreq:
    def test_counts_duplicate_lines(self):
        output = _run(["foo\n", "bar\n", "foo\n"])
        assert "foo" in output
        assert "2" in output

    def test_header_present_by_default(self):
        output = _run(["a\n", "b\n"])
        assert "count" in output

    def test_no_header_suppresses_header(self):
        output = _run(["a\n", "b\n"], no_header=True)
        assert "count" not in output

    def test_top_limits_output_rows(self):
        lines = ["x\n"] * 5 + ["y\n"] * 3 + ["z\n"] * 1
        output = _run(lines, top=1, no_header=True)
        data_lines = [l for l in output.splitlines() if l.strip()]
        assert len(data_lines) == 1
        assert "x" in data_lines[0]

    def test_field_mode_json(self):
        lines = [
            '{"level": "INFO"}\n',
            '{"level": "ERROR"}\n',
            '{"level": "INFO"}\n',
        ]
        output = _run(lines, field="level", no_header=True)
        assert "INFO" in output
        assert "2" in output

    def test_empty_input_returns_zero(self):
        out = io.StringIO()
        args = _ns(files=[])
        # feed empty stdin via monkey-patch
        import sys
        old = sys.stdin
        sys.stdin = io.StringIO("")
        try:
            rc = run_freq(args, out=out)
        finally:
            sys.stdin = old
        assert rc == 0
        assert out.getvalue() == ""

    def test_missing_file_returns_error(self):
        out = io.StringIO()
        args = _ns(files=["/nonexistent/path/file.log"])
        rc = run_freq(args, out=out)
        assert rc == 1
