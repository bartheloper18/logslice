"""Tests for logslice.compact."""

from __future__ import annotations

import io
import json

import pytest

from logslice.compact import compact_lines, compact_file


def _run(lines: list[str]) -> list[str]:
    return list(compact_lines(lines))


# ---------------------------------------------------------------------------
# Plain / non-JSON lines
# ---------------------------------------------------------------------------

def test_plain_line_passed_through():
    result = _run(["hello world\n"])
    assert result == ["hello world\n"]


def test_multiple_plain_lines_passed_through():
    lines = ["alpha\n", "beta\n", "gamma\n"]
    assert _run(lines) == lines


# ---------------------------------------------------------------------------
# Single-line JSON
# ---------------------------------------------------------------------------

def test_single_line_json_compacted():
    line = '{"level": "info",  "msg": "ok"}\n'
    result = _run([line])
    assert len(result) == 1
    assert json.loads(result[0]) == {"level": "info", "msg": "ok"}
    # No extra spaces.
    assert " " not in result[0].rstrip()


def test_single_line_array_compacted():
    line = '[1,  2,   3]\n'
    result = _run([line])
    assert result == ["[1,2,3]\n"]


# ---------------------------------------------------------------------------
# Multi-line JSON
# ---------------------------------------------------------------------------

def test_multiline_object_collapsed():
    lines = [
        "{\n",
        '  "level": "error",\n',
        '  "msg": "boom"\n',
        "}\n",
    ]
    result = _run(lines)
    assert len(result) == 1
    assert json.loads(result[0]) == {"level": "error", "msg": "boom"}


def test_multiline_array_collapsed():
    lines = ["[\n", "  1,\n", "  2,\n", "  3\n", "]\n"]
    result = _run(lines)
    assert len(result) == 1
    assert json.loads(result[0]) == [1, 2, 3]


def test_mixed_plain_and_multiline():
    lines = [
        "start\n",
        "{\n",
        '  "k": "v"\n',
        "}\n",
        "end\n",
    ]
    result = _run(lines)
    assert result[0] == "start\n"
    assert json.loads(result[1]) == {"k": "v"}
    assert result[2] == "end\n"


def test_two_consecutive_multiline_objects():
    lines = [
        "{\n", '"a": 1\n', "}\n",
        "{\n", '"b": 2\n', "}\n",
    ]
    result = _run(lines)
    assert len(result) == 2
    assert json.loads(result[0]) == {"a": 1}
    assert json.loads(result[1]) == {"b": 2}


# ---------------------------------------------------------------------------
# compact_file helper
# ---------------------------------------------------------------------------

def test_compact_file_returns_line_count():
    src = io.StringIO('{"x": 1}\nplain\n')
    dst = io.StringIO()
    count = compact_file(src, dst)
    assert count == 2


def test_compact_file_output_correct():
    src = io.StringIO("[\n  1,\n  2\n]\n")
    dst = io.StringIO()
    compact_file(src, dst)
    dst.seek(0)
    assert json.loads(dst.read()) == [1, 2]
