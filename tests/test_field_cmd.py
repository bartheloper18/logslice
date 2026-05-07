"""Tests for logslice.field_cmd."""

import argparse
import io
import pytest
from logslice.field_cmd import build_field_parser, run_field


def _ns(**kwargs):
    defaults = {"field": "level", "value": None, "file": None, "ignore_case": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(lines, **kwargs):
    ns = _ns(**kwargs)
    out = io.StringIO()
    err = io.StringIO()

    import unittest.mock as mock
    import sys

    stdin_data = io.StringIO("".join(l + "\n" for l in lines))
    with mock.patch("sys.stdin", stdin_data):
        rc = run_field(ns, out=out, err=err)
    return rc, out.getvalue(), err.getvalue()


class TestBuildFieldParser:
    def test_returns_parser(self):
        p = build_field_parser()
        assert isinstance(p, argparse.ArgumentParser)

    def test_field_positional(self):
        p = build_field_parser()
        args = p.parse_args(["level"])
        assert args.field == "level"

    def test_value_optional(self):
        p = build_field_parser()
        args = p.parse_args(["level"])
        assert args.value is None

    def test_ignore_case_flag(self):
        p = build_field_parser()
        args = p.parse_args(["level", "-i"])
        assert args.ignore_case is True


class TestRunField:
    def test_filter_by_value(self):
        lines = ["level=INFO msg=a", "level=ERROR msg=b"]
        rc, out, _ = _run(lines, field="level", value="INFO")
        assert rc == 0
        assert "level=INFO msg=a" in out
        assert "level=ERROR" not in out

    def test_print_field_values_when_no_value(self):
        lines = ["level=INFO", "level=ERROR"]
        rc, out, _ = _run(lines, field="level", value=None)
        assert rc == 0
        assert "INFO" in out
        assert "ERROR" in out

    def test_ignore_case_filter(self):
        lines = ["level=info", "level=ERROR"]
        rc, out, _ = _run(lines, field="level", value="INFO", ignore_case=True)
        assert "level=info" in out
        assert "ERROR" not in out

    def test_json_lines_filtered(self):
        lines = ['{"level":"INFO","msg":"ok"}', '{"level":"ERROR","msg":"fail"}']
        rc, out, _ = _run(lines, field="level", value="ERROR")
        assert "fail" in out
        assert "ok" not in out

    def test_missing_field_lines_excluded(self):
        lines = ["no fields here", "level=INFO"]
        rc, out, _ = _run(lines, field="level", value="INFO")
        assert out.strip() == "level=INFO"
