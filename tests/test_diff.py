"""Tests for logslice.diff."""

from __future__ import annotations

import pytest

from logslice.diff import DiffLine, diff_lines, format_diff


LEFT = [
    "2024-01-01T00:00:01 INFO  server started\n",
    "2024-01-01T00:00:02 INFO  listening on :8080\n",
    "2024-01-01T00:00:03 ERROR disk full\n",
]

RIGHT = [
    "2024-01-01T00:00:01 INFO  server started\n",
    "2024-01-01T00:00:04 WARN  high memory\n",
    "2024-01-01T00:00:05 INFO  listening on :8080\n",
]


def _sides(entries):
    return [e.side for e in entries]


def test_common_line_marked_both():
    entries = list(diff_lines(LEFT, RIGHT))
    both = [e for e in entries if e.side == "both"]
    assert len(both) >= 1
    assert any("server started" in e.text for e in both)


def test_left_only_line():
    entries = list(diff_lines(LEFT, RIGHT))
    left_only = [e for e in entries if e.side == "left"]
    texts = [e.text for e in left_only]
    assert any("disk full" in t for t in texts)


def test_right_only_line():
    entries = list(diff_lines(LEFT, RIGHT))
    right_only = [e for e in entries if e.side == "right"]
    texts = [e.text for e in right_only]
    assert any("high memory" in t for t in texts)


def test_lineno_left_set_for_left_entries():
    entries = list(diff_lines(LEFT, RIGHT))
    for e in entries:
        if e.side == "left":
            assert e.lineno_left is not None
            assert e.lineno_right is None


def test_lineno_right_set_for_right_entries():
    entries = list(diff_lines(LEFT, RIGHT))
    for e in entries:
        if e.side == "right":
            assert e.lineno_right is not None
            assert e.lineno_left is None


def test_identical_files_all_both():
    lines = ["INFO hello\n", "ERROR oops\n"]
    entries = list(diff_lines(lines, lines))
    assert all(e.side == "both" for e in entries)


def test_empty_left():
    entries = list(diff_lines([], ["INFO hello\n"]))
    assert len(entries) == 1
    assert entries[0].side == "right"


def test_empty_right():
    entries = list(diff_lines(["INFO hello\n"], []))
    assert len(entries) == 1
    assert entries[0].side == "left"


def test_ignore_timestamps_treats_same_message_as_equal():
    left = ["2024-01-01T10:00:00 INFO  server started\n"]
    right = ["2024-01-02T11:00:00 INFO  server started\n"]
    entries = list(diff_lines(left, right, ignore_timestamps=True))
    assert len(entries) == 1
    assert entries[0].side == "both"


def test_format_diff_prefix_left():
    entries = [DiffLine(side="left", lineno_left=1, lineno_right=None, text="foo")]
    out = list(format_diff(entries))
    assert out[0].startswith("< ")


def test_format_diff_prefix_right():
    entries = [DiffLine(side="right", lineno_left=None, lineno_right=1, text="bar")]
    out = list(format_diff(entries))
    assert out[0].startswith("> ")


def test_format_diff_only_filter():
    entries = [
        DiffLine(side="left", lineno_left=1, lineno_right=None, text="a"),
        DiffLine(side="right", lineno_left=None, lineno_right=1, text="b"),
        DiffLine(side="both", lineno_left=2, lineno_right=2, text="c"),
    ]
    out = list(format_diff(entries, only="left"))
    assert len(out) == 1
    assert "a" in out[0]


def test_format_diff_color_contains_escape():
    entries = [DiffLine(side="left", lineno_left=1, lineno_right=None, text="oops")]
    out = list(format_diff(entries, color=True))
    assert "\033[" in out[0]
