"""Tests for logslice.template and logslice.template_cmd."""

from __future__ import annotations

import argparse
import io
import textwrap

import pytest

from logslice.template import render_template, template_lines, template_file
from logslice.template_cmd import build_template_parser, run_template


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

class TestRenderTemplate:
    def test_simple_field_substituted(self):
        result = render_template("{level}: {message}", {"level": "INFO", "message": "ok"}, "raw", 1)
        assert result == "INFO: ok"

    def test_special_line_placeholder(self):
        result = render_template("{_line}", {}, "hello world\n", 1)
        assert result == "hello world"

    def test_special_lineno_placeholder(self):
        result = render_template("#{_lineno}", {}, "x", 42)
        assert result == "#42"

    def test_missing_placeholder_left_as_is(self):
        result = render_template("{missing}", {}, "raw", 1)
        assert result == "{missing}"

    def test_numeric_field_value_converted(self):
        result = render_template("{count}", {"count": 7}, "raw", 1)
        assert result == "7"


# ---------------------------------------------------------------------------
# template_lines
# ---------------------------------------------------------------------------

def _lines(text: str):
    return text.splitlines(keepends=True)


def test_json_fields_extracted():
    lines = _lines('{"level": "ERROR", "msg": "boom"}\n')
    result = list(template_lines(lines, "{level}: {msg}"))
    assert result == ["ERROR: boom\n"]


def test_kv_fields_extracted():
    lines = _lines("level=WARN msg=disk_full\n")
    result = list(template_lines(lines, "[{level}] {msg}"))
    assert result == ["[WARN] disk_full\n"]


def test_plain_line_uses_line_placeholder():
    lines = _lines("just a plain log line\n")
    result = list(template_lines(lines, "{_line}"))
    assert result == ["just a plain log line\n"]


def test_multiple_lines_lineno_increments():
    lines = _lines("a\nb\nc\n")
    result = list(template_lines(lines, "{_lineno}:{_line}"))
    assert result == ["1:a\n", "2:b\n", "3:c\n"]


def test_preserve_newline_false():
    lines = _lines("hello\n")
    result = list(template_lines(lines, "{_line}", preserve_newline=False))
    assert result == ["hello"]


# ---------------------------------------------------------------------------
# template_file
# ---------------------------------------------------------------------------

def test_template_file(tmp_path):
    log = tmp_path / "app.log"
    log.write_text('{"level":"INFO","msg":"started"}\n', encoding="utf-8")
    out = io.StringIO()
    template_file(str(log), "{level} - {msg}", out=out)
    assert out.getvalue() == "INFO - started\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    defaults = {"template": "{_line}", "file": None, "output": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(ns, stdin_text=""):
    import unittest.mock as mock
    out = io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(stdin_text)):
        code = run_template(ns, out=out)
    return code, out.getvalue()


def test_returns_parser():
    p = build_template_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_stdin_rendered():
    code, output = _run(_ns(template="[{_lineno}] {_line}"), stdin_text="hello\nworld\n")
    assert code == 0
    assert output == "[1] hello\n[2] world\n"


def test_file_rendered(tmp_path):
    log = tmp_path / "t.log"
    log.write_text("level=INFO msg=ready\n", encoding="utf-8")
    out = io.StringIO()
    ns = _ns(template="{level}: {msg}", file=str(log))
    code = run_template(ns, out=out)
    assert code == 0
    assert out.getvalue() == "INFO: ready\n"


def test_missing_file_returns_1():
    ns = _ns(template="{_line}", file="/nonexistent/file.log")
    out = io.StringIO()
    code = run_template(ns, out=out)
    assert code == 1
