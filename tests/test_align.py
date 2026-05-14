"""Tests for logslice.align and logslice.align_cmd."""

from __future__ import annotations

import argparse
import io
import textwrap

import pytest

from logslice.align import align_lines, align_file
from logslice.align_cmd import build_align_parser, run_align


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _run(lines, keys, sep="  ", missing="-"):
    return list(align_lines(lines, keys, separator=sep, missing=missing))


# ---------------------------------------------------------------------------
# align_lines — JSON input
# ---------------------------------------------------------------------------

def test_json_single_key():
    lines = ['{"level": "INFO", "msg": "ok"}\n']
    result = _run(lines, ["level"])
    assert result == ["INFO\n"]


def test_json_multiple_keys():
    lines = ['{"level": "INFO", "msg": "started"}\n',
             '{"level": "ERROR", "msg": "boom"}\n']
    result = _run(lines, ["level", "msg"])
    # "ERROR" is wider than "INFO" → INFO padded to 5
    assert result[0].startswith("INFO ")
    assert result[1].startswith("ERROR")


def test_json_missing_field_uses_placeholder():
    lines = ['{"level": "WARN"}\n']
    result = _run(lines, ["level", "msg"])
    assert "-" in result[0]


def test_json_custom_missing():
    lines = ['{"level": "DEBUG"}\n']
    result = _run(lines, ["level", "msg"], missing="N/A")
    assert "N/A" in result[0]


# ---------------------------------------------------------------------------
# align_lines — key=value input
# ---------------------------------------------------------------------------

def test_kv_single_key():
    lines = ["level=INFO msg=hello\n"]
    result = _run(lines, ["level"])
    assert result[0].strip() == "INFO"


def test_kv_multiple_keys_aligned():
    lines = [
        "level=INFO msg=short\n",
        "level=WARNING msg=a_very_long_message\n",
    ]
    result = _run(lines, ["level", "msg"])
    # columns must be equal width across both rows
    col_widths = [len(col) for col in result[0].rstrip("\n").split("  ")]
    col_widths2 = [len(col) for col in result[1].rstrip("\n").split("  ")]
    assert col_widths == col_widths2


# ---------------------------------------------------------------------------
# align_lines — non-structured passthrough
# ---------------------------------------------------------------------------

def test_plain_line_passed_through():
    lines = ["just a plain log line\n"]
    result = _run(lines, ["level"])
    assert result == ["just a plain log line\n"]


def test_plain_line_gets_newline_appended():
    lines = ["no newline"]
    result = _run(lines, ["level"])
    assert result[0].endswith("\n")


# ---------------------------------------------------------------------------
# align_file
# ---------------------------------------------------------------------------

def test_align_file(tmp_path):
    f = tmp_path / "sample.log"
    f.write_text('{"level": "INFO", "msg": "boot"}\n{"level": "ERROR", "msg": "crash"}\n')
    result = list(align_file(str(f), ["level", "msg"]))
    assert len(result) == 2
    assert "INFO" in result[0]
    assert "ERROR" in result[1]


# ---------------------------------------------------------------------------
# align_cmd
# ---------------------------------------------------------------------------

def test_build_align_parser_returns_parser():
    sub = argparse.ArgumentParser().add_subparsers()
    p = build_align_parser(sub)
    assert isinstance(p, argparse.ArgumentParser)


def test_run_align_from_file(tmp_path):
    f = tmp_path / "a.log"
    f.write_text('{"level": "INFO", "msg": "hi"}\n')
    out = io.StringIO()
    run_align(["level", "msg"], file=str(f), out=out)
    assert "INFO" in out.getvalue()
    assert "hi" in out.getvalue()


def test_run_align_custom_sep(tmp_path):
    f = tmp_path / "b.log"
    f.write_text('{"level": "DEBUG", "msg": "test"}\n')
    out = io.StringIO()
    run_align(["level", "msg"], file=str(f), sep="|", out=out)
    assert "|" in out.getvalue()
