"""Tests for logslice.convert."""
from __future__ import annotations

import json
import pytest

from logslice.convert import convert_line, convert_lines, convert_file


# ---------------------------------------------------------------------------
# convert_line — JSON input
# ---------------------------------------------------------------------------

def test_json_to_kv():
    line = json.dumps({"level": "INFO", "msg": "hello"}) + "\n"
    result = convert_line(line, "kv")
    assert "level=INFO" in result
    assert "msg=hello" in result


def test_json_to_plain():
    line = json.dumps({"level": "INFO", "msg": "hello"}) + "\n"
    result = convert_line(line, "plain")
    assert "INFO" in result
    assert "hello" in result


def test_json_to_json_roundtrip():
    data = {"ts": "2024-01-01", "level": "ERROR", "msg": "boom"}
    line = json.dumps(data) + "\n"
    result = convert_line(line, "json")
    assert json.loads(result) == data


# ---------------------------------------------------------------------------
# convert_line — kv input
# ---------------------------------------------------------------------------

def test_kv_to_json():
    line = "level=INFO msg=hello\n"
    result = convert_line(line, "json")
    obj = json.loads(result)
    assert obj["level"] == "INFO"
    assert obj["msg"] == "hello"


def test_kv_to_plain():
    line = "level=INFO msg=hello\n"
    result = convert_line(line, "plain")
    assert "INFO" in result
    assert "hello" in result


# ---------------------------------------------------------------------------
# convert_line — plain / unparseable input
# ---------------------------------------------------------------------------

def test_plain_to_json_wraps_message():
    line = "some plain log line\n"
    result = convert_line(line, "json")
    obj = json.loads(result)
    assert obj["message"] == "some plain log line"


def test_plain_to_kv_wraps_message():
    line = "some plain log line\n"
    result = convert_line(line, "kv")
    assert "message=" in result


def test_plain_to_plain_unchanged():
    line = "some plain log line\n"
    assert convert_line(line, "plain") == line


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_unsupported_target_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        convert_line("hello\n", "xml")


def test_result_ends_with_newline():
    for fmt in ("json", "kv", "plain"):
        assert convert_line("key=val\n", fmt).endswith("\n")


# ---------------------------------------------------------------------------
# convert_lines
# ---------------------------------------------------------------------------

def test_convert_lines_yields_all():
    lines = [
        json.dumps({"a": 1}) + "\n",
        json.dumps({"b": 2}) + "\n",
    ]
    results = list(convert_lines(lines, "kv"))
    assert len(results) == 2
    assert "a=1" in results[0]
    assert "b=2" in results[1]


# ---------------------------------------------------------------------------
# convert_file
# ---------------------------------------------------------------------------

def test_convert_file(tmp_path):
    src = tmp_path / "input.log"
    src.write_text(
        json.dumps({"level": "INFO", "msg": "hi"}) + "\n"
        + json.dumps({"level": "WARN", "msg": "uh"}) + "\n"
    )
    out_lines = []

    class _FakeOut:
        def write(self, s):
            out_lines.append(s)

    count = convert_file(str(src), "kv", _FakeOut())
    assert count == 2
    assert any("level=INFO" in l for l in out_lines)
