"""Tests for logslice.normalize."""

from __future__ import annotations

import io
import json
import pytest

from logslice.normalize import (
    normalize_line,
    normalize_lines,
    normalize_file,
)


# ---------------------------------------------------------------------------
# normalize_line – JSON target
# ---------------------------------------------------------------------------

class TestNormalizeLineToJson:
    def test_kv_to_json(self):
        result = normalize_line("level=info msg=started", target="json")
        obj = json.loads(result)
        assert obj == {"level": "info", "msg": "started"}

    def test_json_roundtrip(self):
        raw = json.dumps({"ts": "2024-01-01", "level": "error"})
        result = normalize_line(raw, target="json")
        assert json.loads(result) == {"ts": "2024-01-01", "level": "error"}

    def test_kv_quoted_values(self):
        result = normalize_line('msg="hello world" code=42', target="json")
        obj = json.loads(result)
        assert obj["msg"] == "hello world"
        assert obj["code"] == "42"

    def test_newline_preserved(self):
        result = normalize_line("level=warn\n", target="json")
        assert result.endswith("\n")
        obj = json.loads(result.rstrip("\n"))
        assert obj["level"] == "warn"

    def test_unparseable_line_unchanged(self):
        line = "plain text without structure\n"
        assert normalize_line(line, target="json") == line

    def test_unknown_target_raises(self):
        with pytest.raises(ValueError, match="Unknown target"):
            normalize_line("level=info", target="csv")


# ---------------------------------------------------------------------------
# normalize_line – kv target
# ---------------------------------------------------------------------------

class TestNormalizeLineToKv:
    def test_json_to_kv(self):
        raw = json.dumps({"level": "info", "msg": "ok"})
        result = normalize_line(raw, target="kv")
        assert "level=info" in result
        assert "msg=ok" in result

    def test_kv_with_spaces_quoted(self):
        raw = json.dumps({"msg": "hello world"})
        result = normalize_line(raw, target="kv")
        assert 'msg="hello world"' in result

    def test_newline_preserved(self):
        raw = json.dumps({"x": "1"}) + "\n"
        result = normalize_line(raw, target="kv")
        assert result.endswith("\n")


# ---------------------------------------------------------------------------
# normalize_lines
# ---------------------------------------------------------------------------

def test_normalize_lines_yields_all():
    lines = ["level=info msg=a\n", "level=error msg=b\n"]
    results = list(normalize_lines(iter(lines), target="json"))
    assert len(results) == 2
    for r in results:
        obj = json.loads(r.rstrip("\n"))
        assert "level" in obj


def test_normalize_lines_skips_unparseable():
    lines = ["level=info\n", "just plain text\n"]
    results = list(normalize_lines(iter(lines), target="json"))
    assert json.loads(results[0].rstrip("\n")) == {"level": "info"}
    assert results[1] == "just plain text\n"


# ---------------------------------------------------------------------------
# normalize_file
# ---------------------------------------------------------------------------

def test_normalize_file_returns_count():
    src = io.StringIO("level=info\nlevel=warn\n")
    dest = io.StringIO()
    count = normalize_file(src, dest, target="json")
    assert count == 2


def test_normalize_file_content():
    src = io.StringIO("level=debug msg=test\n")
    dest = io.StringIO()
    normalize_file(src, dest, target="json")
    dest.seek(0)
    obj = json.loads(dest.read().rstrip("\n"))
    assert obj["level"] == "debug"
    assert obj["msg"] == "test"
