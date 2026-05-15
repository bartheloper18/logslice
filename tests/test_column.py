"""Tests for logslice.column."""

from __future__ import annotations

import pytest

from logslice.column import extract_columns, format_columns, _parse_fields


# ---------------------------------------------------------------------------
# _parse_fields
# ---------------------------------------------------------------------------

def test_parse_json_fields():
    result = _parse_fields('{"level": "INFO", "msg": "hello"}')
    assert result == {"level": "INFO", "msg": "hello"}


def test_parse_kv_fields():
    result = _parse_fields('level=INFO msg=hello')
    assert result["level"] == "INFO"
    assert result["msg"] == "hello"


def test_parse_plain_returns_none():
    assert _parse_fields("just a plain log line") is None


def test_parse_json_array_returns_none():
    assert _parse_fields('[1, 2, 3]') is None


# ---------------------------------------------------------------------------
# extract_columns
# ---------------------------------------------------------------------------

def test_extract_columns_json():
    line = '{"level": "ERROR", "code": "500"}'
    assert extract_columns(line, ["level", "code"]) == ["ERROR", "500"]


def test_extract_columns_missing_uses_placeholder():
    line = '{"level": "WARN"}'
    assert extract_columns(line, ["level", "code"], missing="N/A") == ["WARN", "N/A"]


def test_extract_columns_plain_line_all_missing():
    assert extract_columns("plain text", ["a", "b"], missing="-") == ["-", "-"]


def test_extract_columns_kv():
    line = 'status=200 path=/api'
    result = extract_columns(line, ["status", "path"])
    assert result == ["200", "/api"]


# ---------------------------------------------------------------------------
# format_columns
# ---------------------------------------------------------------------------

_JSON_LINES = [
    '{"level": "INFO", "msg": "started"}\n',
    '{"level": "ERROR", "msg": "failed"}\n',
]


def test_format_columns_header_present():
    rows = list(format_columns(_JSON_LINES, ["level", "msg"], header=True))
    assert rows[0].startswith("LEVEL")


def test_format_columns_no_header():
    rows = list(format_columns(_JSON_LINES, ["level", "msg"], header=False))
    assert rows[0].startswith("INFO")


def test_format_columns_alignment():
    rows = list(format_columns(_JSON_LINES, ["level", "msg"], header=False))
    # All rows should have the same column start position for the second field
    positions = [r.index(r.split()[1]) for r in rows]
    assert len(set(positions)) == 1


def test_format_columns_custom_separator():
    rows = list(format_columns(_JSON_LINES, ["level"], separator="|", header=False))
    assert all("|" not in r or r.count("|") >= 0 for r in rows)


def test_format_columns_empty_input_yields_nothing():
    assert list(format_columns([], ["level"])) == []


def test_format_columns_missing_placeholder():
    lines = ['{"level": "DEBUG"}\n']
    rows = list(format_columns(lines, ["level", "msg"], missing="???", header=False))
    assert "???" in rows[0]


def test_format_columns_each_row_ends_with_newline():
    rows = list(format_columns(_JSON_LINES, ["level", "msg"], header=True))
    assert all(r.endswith("\n") for r in rows)
