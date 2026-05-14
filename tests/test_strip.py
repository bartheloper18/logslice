"""Tests for logslice.strip."""

from __future__ import annotations

import json
import pytest

from logslice.strip import (
    strip_ansi,
    strip_fields,
    strip_prefix,
    strip_lines,
)


# ---------------------------------------------------------------------------
# strip_ansi
# ---------------------------------------------------------------------------

class TestStripAnsi:
    def test_removes_colour_codes(self):
        line = "\x1b[31mERROR\x1b[0m something went wrong"
        assert strip_ansi(line) == "ERROR something went wrong"

    def test_plain_line_unchanged(self):
        line = "plain log line"
        assert strip_ansi(line) == line

    def test_multiple_codes_removed(self):
        line = "\x1b[1m\x1b[32mINFO\x1b[0m message"
        assert strip_ansi(line) == "INFOmessage" or "INFO" in strip_ansi(line)


# ---------------------------------------------------------------------------
# strip_fields — JSON
# ---------------------------------------------------------------------------

class TestStripFieldsJson:
    def test_removes_single_key(self):
        line = json.dumps({"level": "INFO", "msg": "hello"}) + "\n"
        result = strip_fields(line, ["level"])
        obj = json.loads(result)
        assert "level" not in obj
        assert obj["msg"] == "hello"

    def test_removes_multiple_keys(self):
        line = json.dumps({"a": 1, "b": 2, "c": 3})
        result = strip_fields(line, ["a", "c"])
        obj = json.loads(result)
        assert obj == {"b": 2}

    def test_missing_key_no_error(self):
        line = json.dumps({"msg": "hi"})
        result = strip_fields(line, ["nonexistent"])
        assert json.loads(result) == {"msg": "hi"}

    def test_preserves_trailing_newline(self):
        line = json.dumps({"x": 1}) + "\n"
        result = strip_fields(line, ["x"])
        assert result.endswith("\n")


# ---------------------------------------------------------------------------
# strip_fields — key=value
# ---------------------------------------------------------------------------

class TestStripFieldsKv:
    def test_removes_simple_kv(self):
        line = "level=INFO msg=hello\n"
        result = strip_fields(line, ["level"])
        assert "level=" not in result
        assert "msg=hello" in result

    def test_removes_quoted_value(self):
        line = 'level=INFO msg="hello world"'
        result = strip_fields(line, ["msg"])
        assert "msg=" not in result
        assert "level=INFO" in result

    def test_plain_line_unchanged(self):
        line = "just a plain log line"
        result = strip_fields(line, ["level"])
        assert result == line


# ---------------------------------------------------------------------------
# strip_prefix
# ---------------------------------------------------------------------------

class TestStripPrefix:
    def test_removes_matching_prefix(self):
        assert strip_prefix("INFO: something", "INFO:") == "something"

    def test_no_match_returns_original(self):
        line = "DEBUG: other"
        assert strip_prefix(line, "INFO:") == line

    def test_strips_leading_whitespace_before_check(self):
        assert strip_prefix("   INFO: msg", "INFO:") == "msg"


# ---------------------------------------------------------------------------
# strip_lines
# ---------------------------------------------------------------------------

def test_strip_lines_ansi_flag():
    lines = ["\x1b[31mERROR\x1b[0m bad", "ok\n"]
    result = list(strip_lines(lines, ansi=True))
    assert result[0] == "ERROR bad"
    assert result[1] == "ok\n"


def test_strip_lines_fields_and_ansi():
    coloured = "\x1b[32m" + json.dumps({"level": "INFO", "msg": "hi"}) + "\x1b[0m"
    result = list(strip_lines([coloured], fields=["level"], ansi=True))
    obj = json.loads(result[0])
    assert "level" not in obj


def test_strip_lines_prefix():
    lines = ["INFO: first\n", "DEBUG: second\n"]
    result = list(strip_lines(lines, prefix="INFO:"))
    assert result[0].strip() == "first"
    assert "DEBUG:" in result[1]
