"""Tests for logslice.sort and logslice.sort_cmd."""

from __future__ import annotations

import io
import argparse
import textwrap

import pytest

from logslice.sort import sort_lines, sort_file
from logslice.sort_cmd import build_sort_parser, run_sort


LINES_TS = [
    "2024-01-03T10:00:00 INFO  third\n",
    "2024-01-01T08:00:00 INFO  first\n",
    "2024-01-02T09:00:00 INFO  second\n",
]

LINES_NO_TS = [
    "no timestamp here\n",
    "also no timestamp\n",
]

LINES_KV = [
    "level=info user=bob score=30\n",
    "level=warn user=alice score=10\n",
    "level=error user=carol score=20\n",
]

LINES_JSON = [
    '{"level":"info","user":"bob"}\n',
    '{"level":"error","user":"alice"}\n',
    '{"level":"warn","user":"carol"}\n',
]


# ---------------------------------------------------------------------------
# sort_lines — timestamp
# ---------------------------------------------------------------------------

def test_sort_by_timestamp_ascending():
    result = sort_lines(LINES_TS, key="timestamp")
    assert "first" in result[0]
    assert "second" in result[1]
    assert "third" in result[2]


def test_sort_by_timestamp_descending():
    result = sort_lines(LINES_TS, key="timestamp", reverse=True)
    assert "third" in result[0]
    assert "first" in result[2]


def test_lines_without_timestamp_sorted_last():
    mixed = LINES_TS[:1] + LINES_NO_TS + LINES_TS[1:]
    result = sort_lines(mixed, key="timestamp")
    # timestamped lines come before non-timestamped
    ts_done = False
    for line in result:
        if "no timestamp" in line or "also no" in line:
            ts_done = True
        else:
            assert not ts_done, "timestamped line appeared after non-timestamped"


def test_empty_input_returns_empty():
    assert sort_lines([], key="timestamp") == []


# ---------------------------------------------------------------------------
# sort_lines — field
# ---------------------------------------------------------------------------

def test_sort_kv_by_field():
    result = sort_lines(LINES_KV, key="user")
    users = [ln.split("user=")[1].split()[0] for ln in result]
    assert users == sorted(users)


def test_sort_json_by_field():
    result = sort_lines(LINES_JSON, key="level")
    import json
    levels = [json.loads(ln)["level"] for ln in result]
    assert levels == sorted(levels)


def test_sort_json_by_field_reverse():
    result = sort_lines(LINES_JSON, key="level", reverse=True)
    import json
    levels = [json.loads(ln)["level"] for ln in result]
    assert levels == sorted(levels, reverse=True)


def test_missing_field_sorts_first():
    lines = ["level=info user=bob\n", "no fields here\n", "level=warn user=alice\n"]
    result = sort_lines(lines, key="user")
    # missing field => empty string => sorts first
    assert "no fields" in result[0]


# ---------------------------------------------------------------------------
# sort_file
# ---------------------------------------------------------------------------

def test_sort_file(tmp_path):
    f = tmp_path / "app.log"
    f.write_text("".join(LINES_TS))
    out = io.StringIO()
    sort_file(str(f), out, key="timestamp")
    lines = out.getvalue().splitlines()
    assert "first" in lines[0]
    assert "third" in lines[-1]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _ns(**kw) -> argparse.Namespace:
    defaults = {"file": None, "key": "timestamp", "reverse": False}
    defaults.update(kw)
    return argparse.Namespace(**defaults)


def _run(args, stdin_lines=None):
    out = io.StringIO()
    if stdin_lines is not None:
        import unittest.mock as mock
        with mock.patch("sys.stdin", io.StringIO("".join(stdin_lines))):
            rc = run_sort(args, out=out)
    else:
        rc = run_sort(args, out=out)
    return rc, out.getvalue()


def test_build_sort_parser_returns_parser():
    p = build_sort_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_defaults():
    p = build_sort_parser()
    args = p.parse_args([])
    assert args.key == "timestamp"
    assert args.reverse is False
    assert args.file is None


def test_stdin_sort(tmp_path):
    rc, out = _run(_ns(), stdin_lines=LINES_TS)
    assert rc == 0
    assert "first" in out.splitlines()[0]


def test_file_sort(tmp_path):
    f = tmp_path / "app.log"
    f.write_text("".join(LINES_TS))
    rc, out = _run(_ns(file=str(f)))
    assert rc == 0
    assert "first" in out.splitlines()[0]


def test_reverse_flag(tmp_path):
    f = tmp_path / "app.log"
    f.write_text("".join(LINES_TS))
    rc, out = _run(_ns(file=str(f), reverse=True))
    assert rc == 0
    assert "third" in out.splitlines()[0]
