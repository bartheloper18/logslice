"""Tests for logslice.window and logslice.window_cmd."""

from __future__ import annotations

import argparse
import datetime
import io
import textwrap

import pytest

from logslice.window import window_lines
from logslice.window_cmd import build_window_parser, run_window


ANCHOR = datetime.datetime(2024, 6, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)


def _lines(*texts):
    return list(texts)


# ---------------------------------------------------------------------------
# window_lines
# ---------------------------------------------------------------------------

class TestWindowLines:
    def test_line_inside_window_kept(self):
        lines = ["2024-06-01T11:59:30Z INFO hello\n"]
        result = list(window_lines(lines, seconds=60, anchor=ANCHOR))
        assert result == lines

    def test_line_outside_window_dropped(self):
        lines = ["2024-06-01T11:58:59Z INFO old\n"]
        result = list(window_lines(lines, seconds=60, anchor=ANCHOR))
        assert result == []

    def test_line_exactly_at_start_kept(self):
        lines = ["2024-06-01T11:59:00Z INFO boundary\n"]
        result = list(window_lines(lines, seconds=60, anchor=ANCHOR))
        assert result == lines

    def test_line_at_anchor_kept(self):
        lines = ["2024-06-01T12:00:00Z INFO now\n"]
        result = list(window_lines(lines, seconds=60, anchor=ANCHOR))
        assert result == lines

    def test_no_timestamp_line_always_yielded(self):
        lines = ["no timestamp here\n"]
        result = list(window_lines(lines, seconds=60, anchor=ANCHOR))
        assert result == lines

    def test_mixed_lines(self):
        lines = [
            "2024-06-01T11:59:30Z INFO inside\n",
            "2024-06-01T11:58:00Z INFO outside\n",
            "plain text\n",
        ]
        result = list(window_lines(lines, seconds=60, anchor=ANCHOR))
        assert "2024-06-01T11:59:30Z INFO inside\n" in result
        assert "2024-06-01T11:58:00Z INFO outside\n" not in result
        assert "plain text\n" in result

    def test_zero_seconds_raises(self):
        with pytest.raises(ValueError, match="positive"):
            list(window_lines([], seconds=0, anchor=ANCHOR))

    def test_negative_seconds_raises(self):
        with pytest.raises(ValueError):
            list(window_lines([], seconds=-5, anchor=ANCHOR))

    def test_empty_input(self):
        assert list(window_lines([], seconds=60, anchor=ANCHOR)) == []


# ---------------------------------------------------------------------------
# window_cmd
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    defaults = dict(seconds=60.0, file=None, anchor=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(ns, input_text=""):
    out = io.StringIO()
    sys_stdin_backup = __import__("sys").stdin
    import sys
    sys.stdin = io.StringIO(input_text)
    try:
        rc = run_window(ns, out=out)
    finally:
        sys.stdin = sys_stdin_backup
    return rc, out.getvalue()


def test_build_window_parser_returns_parser():
    p = build_window_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_invalid_seconds_returns_error():
    ns = _ns(seconds=-1)
    rc, _ = _run(ns)
    assert rc == 1


def test_invalid_anchor_returns_error():
    ns = _ns(anchor="not-a-date")
    rc, _ = _run(ns)
    assert rc == 1


def test_stdin_filtered_by_window():
    anchor_str = "2024-06-01T12:00:00+00:00"
    inside = "2024-06-01T11:59:30Z INFO hello"
    outside = "2024-06-01T11:50:00Z INFO old"
    ns = _ns(seconds=60, anchor=anchor_str)
    rc, output = _run(ns, input_text=f"{inside}\n{outside}\n")
    assert rc == 0
    assert "hello" in output
    assert "old" not in output
