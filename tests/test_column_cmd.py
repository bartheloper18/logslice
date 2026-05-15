"""Tests for logslice.column_cmd."""

from __future__ import annotations

import io
import textwrap

import pytest

from logslice.column_cmd import build_column_parser, run_column


def _ns(**kwargs):
    defaults = dict(fields=["level", "msg"], file=None,
                    separator="  ", missing="-", no_header=False)
    defaults.update(kwargs)
    import argparse
    return argparse.Namespace(**defaults)


def _run(args, stdin_text=""):
    out = io.StringIO()
    import sys
    import unittest.mock as mock
    with mock.patch("sys.stdin", io.StringIO(stdin_text)):
        rc = run_column(args, out=out)
    return rc, out.getvalue()


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def test_returns_parser():
    import argparse
    p = build_column_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_fields_positional():
    p = build_column_parser()
    ns = p.parse_args(["level", "msg"])
    assert ns.fields == ["level", "msg"]


def test_defaults():
    p = build_column_parser()
    ns = p.parse_args(["level"])
    assert ns.separator == "  "
    assert ns.missing == "-"
    assert ns.no_header is False


def test_no_header_flag():
    p = build_column_parser()
    ns = p.parse_args(["level", "--no-header"])
    assert ns.no_header is True


# ---------------------------------------------------------------------------
# run_column — stdin
# ---------------------------------------------------------------------------

def test_reads_from_stdin():
    data = '{"level": "INFO", "msg": "ok"}\n'
    rc, out = _run(_ns(), stdin_text=data)
    assert rc == 0
    assert "INFO" in out
    assert "ok" in out


def test_header_in_output():
    data = '{"level": "WARN", "msg": "slow"}\n'
    rc, out = _run(_ns(no_header=False), stdin_text=data)
    assert "LEVEL" in out


def test_no_header_suppressed():
    data = '{"level": "WARN", "msg": "slow"}\n'
    rc, out = _run(_ns(no_header=True), stdin_text=data)
    assert "LEVEL" not in out


# ---------------------------------------------------------------------------
# run_column — file
# ---------------------------------------------------------------------------

def test_reads_from_file(tmp_path):
    f = tmp_path / "app.log"
    f.write_text('{"level": "DEBUG", "msg": "boot"}\n')
    rc, out = _run(_ns(file=str(f)))
    assert rc == 0
    assert "DEBUG" in out


def test_missing_file_returns_error():
    rc, out = _run(_ns(file="/nonexistent/path.log"))
    assert rc == 1
