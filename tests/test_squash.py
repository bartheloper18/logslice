"""Tests for logslice.squash."""
from __future__ import annotations

import io
import pytest

from logslice.squash import _signature, squash_lines, squash_file


# ---------------------------------------------------------------------------
# _signature
# ---------------------------------------------------------------------------

def test_signature_replaces_integers():
    assert _signature("connected 42 clients in 3ms") == "connected # clients in #ms"


def test_signature_strips_newline():
    assert "\n" not in _signature("hello 1\n")


def test_signature_no_numbers_unchanged():
    assert _signature("no digits here") == "no digits here"


# ---------------------------------------------------------------------------
# squash_lines
# ---------------------------------------------------------------------------

def _run(lines, **kw):
    return list(squash_lines(lines, **kw))


def test_no_similar_lines_unchanged():
    lines = ["alpha\n", "beta\n", "gamma\n"]
    assert _run(lines) == lines


def test_two_identical_lines_collapsed():
    lines = ["error 42\n", "error 99\n"]
    result = _run(lines)
    assert len(result) == 1
    assert "repeated 2x" in result[0]


def test_collapsed_line_uses_first_representative():
    lines = ["retry 1\n", "retry 2\n", "retry 3\n"]
    result = _run(lines)
    assert result[0].startswith("retry 1")


def test_three_similar_collapsed_with_count():
    lines = ["id=1 status=ok\n"] * 3
    result = _run(lines)
    assert len(result) == 1
    assert "repeated 3x" in result[0]


def test_min_repeat_1_always_collapses():
    lines = ["x 1\n", "x 2\n"]
    result = _run(lines, min_repeat=1)
    assert len(result) == 1


def test_min_repeat_higher_than_run_emits_verbatim():
    lines = ["x 1\n", "x 2\n"]  # run of 2
    result = _run(lines, min_repeat=3)
    assert result == lines


def test_non_adjacent_similar_lines_not_collapsed():
    lines = ["x 1\n", "y 1\n", "x 2\n"]
    result = _run(lines)
    assert result == lines


def test_mixed_runs():
    lines = [
        "conn 1\n",
        "conn 2\n",
        "conn 3\n",
        "done\n",
        "err 1\n",
        "err 2\n",
    ]
    result = _run(lines)
    # First run collapsed, "done" kept, second run collapsed
    assert len(result) == 3
    assert "repeated 3x" in result[0]
    assert result[1] == "done\n"
    assert "repeated 2x" in result[2]


def test_empty_input_returns_empty():
    assert _run([]) == []


def test_single_line_returned_as_is():
    assert _run(["hello\n"]) == ["hello\n"]


# ---------------------------------------------------------------------------
# squash_file
# ---------------------------------------------------------------------------

def test_squash_file(tmp_path):
    f = tmp_path / "app.log"
    f.write_text(
        "connect 1\nconnect 2\nconnect 3\nshutdown\n",
        encoding="utf-8",
    )
    result = list(squash_file(str(f)))
    assert len(result) == 2
    assert "repeated 3x" in result[0]
    assert result[1].strip() == "shutdown"
