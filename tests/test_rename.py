"""Tests for logslice.rename."""

from __future__ import annotations

import json
import pytest

from logslice.rename import rename_fields, rename_lines, rename_file


# ---------------------------------------------------------------------------
# rename_fields – JSON lines
# ---------------------------------------------------------------------------

class TestRenameFieldsJson:
    def test_single_rename(self):
        line = '{"msg":"hello","level":"info"}'
        result = rename_fields(line, {"msg": "message"})
        obj = json.loads(result)
        assert "message" in obj
        assert "msg" not in obj
        assert obj["message"] == "hello"

    def test_multiple_renames(self):
        line = '{"msg":"hi","lvl":"warn","ts":"2024-01-01"}'
        result = rename_fields(line, {"msg": "message", "lvl": "level"})
        obj = json.loads(result)
        assert obj["message"] == "hi"
        assert obj["level"] == "warn"
        assert obj["ts"] == "2024-01-01"

    def test_unknown_field_in_mapping_ignored(self):
        line = '{"msg":"hi"}'
        result = rename_fields(line, {"nonexistent": "x"})
        assert json.loads(result) == {"msg": "hi"}

    def test_trailing_newline_preserved(self):
        line = '{"a":1}\n'
        result = rename_fields(line, {"a": "b"})
        assert result.endswith("\n")
        assert json.loads(result.rstrip("\n")) == {"b": 1}

    def test_no_trailing_newline_not_added(self):
        line = '{"a":1}'
        result = rename_fields(line, {"a": "b"})
        assert not result.endswith("\n")


# ---------------------------------------------------------------------------
# rename_fields – key=value lines
# ---------------------------------------------------------------------------

class TestRenameFieldsKV:
    def test_single_kv_rename(self):
        line = "msg=hello level=info"
        result = rename_fields(line, {"msg": "message"})
        assert "message=hello" in result
        assert "msg=" not in result

    def test_kv_trailing_newline_preserved(self):
        line = "msg=hello\n"
        result = rename_fields(line, {"msg": "message"})
        assert result.endswith("\n")
        assert "message=hello" in result

    def test_kv_unmapped_fields_unchanged(self):
        line = "a=1 b=2"
        result = rename_fields(line, {"a": "alpha"})
        assert "alpha=1" in result
        assert "b=2" in result


# ---------------------------------------------------------------------------
# rename_fields – plain text
# ---------------------------------------------------------------------------

def test_plain_text_unchanged():
    line = "2024-01-01 INFO some log message\n"
    assert rename_fields(line, {"INFO": "info"}) == line


# ---------------------------------------------------------------------------
# rename_lines
# ---------------------------------------------------------------------------

def test_rename_lines_iterates_all():
    lines = [
        '{"a":1}\n',
        '{"a":2}\n',
        '{"a":3}\n',
    ]
    results = list(rename_lines(lines, {"a": "alpha"}))
    assert len(results) == 3
    for r in results:
        obj = json.loads(r)
        assert "alpha" in obj
        assert "a" not in obj


def test_rename_lines_empty_input():
    assert list(rename_lines([], {"a": "b"})) == []


# ---------------------------------------------------------------------------
# rename_file
# ---------------------------------------------------------------------------

def test_rename_file(tmp_path):
    f = tmp_path / "log.jsonl"
    f.write_text('{"msg":"hi","level":"info"}\n{"msg":"bye","level":"warn"}\n')

    import io
    out = io.StringIO()
    rename_file(str(f), {"msg": "message"}, out)
    out.seek(0)
    lines = out.readlines()
    assert len(lines) == 2
    for line in lines:
        obj = json.loads(line)
        assert "message" in obj
        assert "msg" not in obj
