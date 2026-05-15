"""Tests for logslice.cast and logslice.cast_cmd."""
from __future__ import annotations

import json
import types

import pytest

from logslice.cast import cast_value, cast_line, cast_lines
from logslice.cast_cmd import build_cast_parser, run_cast


# ---------------------------------------------------------------------------
# cast_value
# ---------------------------------------------------------------------------

class TestCastValue:
    def test_int_valid(self):
        assert cast_value("42", "int") == 42

    def test_float_valid(self):
        assert cast_value("3.14", "float") == pytest.approx(3.14)

    def test_bool_true_variants(self):
        for v in ("true", "True", "TRUE", "1", "yes"):
            assert cast_value(v, "bool") is True

    def test_bool_false(self):
        assert cast_value("false", "bool") is False

    def test_str_passthrough(self):
        assert cast_value("hello", "str") == "hello"

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown type"):
            cast_value("x", "uuid")

    def test_invalid_int_raises(self):
        with pytest.raises(ValueError):
            cast_value("abc", "int")


# ---------------------------------------------------------------------------
# cast_line
# ---------------------------------------------------------------------------

def _json(obj) -> str:
    return json.dumps(obj, separators=(",", ":"))


def test_cast_line_int_field():
    line = _json({"level": "INFO", "code": "404"}) + "\n"
    result = cast_line(line, "code", "int")
    assert json.loads(result)["code"] == 404


def test_cast_line_preserves_trailing_newline():
    line = _json({"n": "7"}) + "\n"
    assert cast_line(line, "n", "int").endswith("\n")


def test_cast_line_no_newline_preserved():
    line = _json({"n": "7"})
    assert not cast_line(line, "n", "int").endswith("\n")


def test_cast_line_missing_field_unchanged():
    line = _json({"a": "1"}) + "\n"
    assert cast_line(line, "missing", "int") == line


def test_cast_line_non_json_unchanged():
    line = "plain text line\n"
    assert cast_line(line, "field", "int") == line


def test_cast_line_bad_value_unchanged():
    line = _json({"n": "not-a-number"}) + "\n"
    assert cast_line(line, "n", "int") == line


# ---------------------------------------------------------------------------
# cast_lines
# ---------------------------------------------------------------------------

def test_cast_lines_multiple():
    lines = [
        _json({"x": "1"}) + "\n",
        _json({"x": "2"}) + "\n",
        "plain\n",
    ]
    results = list(cast_lines(lines, "x", "int"))
    assert json.loads(results[0])["x"] == 1
    assert json.loads(results[1])["x"] == 2
    assert results[2] == "plain\n"


# ---------------------------------------------------------------------------
# cast_cmd
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    defaults = {"field": "n", "type": "int", "file": None, "output": None}
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _run(args, lines):
    import io
    from unittest.mock import patch
    buf = io.StringIO()
    with patch("logslice.cast_cmd.sys.stdin", io.StringIO("".join(lines))):
        run_cast(args, out=buf)
    return buf.getvalue()


def test_cmd_stdin_to_stdout():
    lines = [_json({"n": "5"}) + "\n"]
    out = _run(_ns(), lines)
    assert json.loads(out.strip())["n"] == 5


def test_build_cast_parser_returns_parser():
    p = build_cast_parser()
    assert p is not None


def test_build_cast_parser_defaults():
    p = build_cast_parser()
    args = p.parse_args(["score", "float"])
    assert args.field == "score"
    assert args.type == "float"
    assert args.file is None
    assert args.output is None
