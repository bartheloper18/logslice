"""Tests for logslice.unique and logslice.unique_cmd."""

from __future__ import annotations

import io
import textwrap
from types import SimpleNamespace

import pytest

from logslice.unique import unique_lines, unique_values, _parse_fields
from logslice.unique_cmd import run_unique


# ---------------------------------------------------------------------------
# _parse_fields
# ---------------------------------------------------------------------------

def test_parse_json_returns_dict():
    result = _parse_fields('{"level": "info", "msg": "ok"}')
    assert result == {"level": "info", "msg": "ok"}


def test_parse_kv_returns_dict():
    result = _parse_fields('level=info msg=hello')
    assert result is not None
    assert result["level"] == "info"


def test_parse_plain_returns_none():
    assert _parse_fields("just a plain log line") is None


# ---------------------------------------------------------------------------
# unique_lines — full-line deduplication
# ---------------------------------------------------------------------------

def test_no_duplicates_unchanged():
    lines = ["alpha\n", "beta\n", "gamma\n"]
    assert list(unique_lines(lines)) == lines


def test_adjacent_duplicates_removed():
    lines = ["alpha\n", "alpha\n", "beta\n"]
    assert list(unique_lines(lines)) == ["alpha\n", "beta\n"]


def test_non_adjacent_duplicates_removed():
    lines = ["alpha\n", "beta\n", "alpha\n"]
    assert list(unique_lines(lines)) == ["alpha\n", "beta\n"]


def test_ignore_case_deduplicates():
    lines = ["Alpha\n", "ALPHA\n", "beta\n"]
    assert list(unique_lines(lines, ignore_case=True)) == ["Alpha\n", "beta\n"]


# ---------------------------------------------------------------------------
# unique_lines — field-based deduplication
# ---------------------------------------------------------------------------

JSON_LINES = [
    '{"level": "info", "msg": "started"}\n',
    '{"level": "error", "msg": "boom"}\n',
    '{"level": "info", "msg": "done"}\n',
]


def test_field_dedup_keeps_first_occurrence():
    result = list(unique_lines(JSON_LINES, field="level"))
    assert len(result) == 2
    assert result[0] == JSON_LINES[0]
    assert result[1] == JSON_LINES[1]


def test_field_missing_line_always_emitted():
    lines = ['{"level": "info"}\n', "plain line\n", '{"level": "info"}\n']
    result = list(unique_lines(lines, field="level"))
    # first json line + plain (no field) + duplicate json dropped
    assert result == ['{"level": "info"}\n', "plain line\n"]


def test_field_ignore_case():
    lines = ['{"level": "INFO"}\n', '{"level": "info"}\n']
    result = list(unique_lines(lines, field="level", ignore_case=True))
    assert len(result) == 1


# ---------------------------------------------------------------------------
# unique_values
# ---------------------------------------------------------------------------

def test_unique_values_extracts_distinct():
    result = list(unique_values(JSON_LINES, field="level"))
    assert result == ["info", "error"]


def test_unique_values_skips_non_structured():
    lines = ["plain\n"] + JSON_LINES
    result = list(unique_values(lines, field="level"))
    assert "plain" not in result


# ---------------------------------------------------------------------------
# run_unique (cmd layer)
# ---------------------------------------------------------------------------

def test_run_unique_full_lines():
    src = io.StringIO("a\nb\na\nc\n")
    out = io.StringIO()
    rc = run_unique(field=None, source=src, out=out)
    assert rc == 0
    assert out.getvalue() == "a\nb\nc\n"


def test_run_unique_values_only():
    src = io.StringIO("".join(JSON_LINES))
    out = io.StringIO()
    rc = run_unique(field="level", source=src, out=out, values_only=True)
    assert rc == 0
    assert out.getvalue() == "info\nerror\n"
