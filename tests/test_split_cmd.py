"""Tests for logslice.split_cmd."""

from __future__ import annotations

import argparse
import io
import os
from unittest.mock import patch

import pytest

from logslice.split_cmd import build_split_parser, run_split


def _ns(**kwargs) -> argparse.Namespace:
    defaults = dict(file=None, output_dir=".", prefix="split", suffix=".log",
                    field=None, pattern=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(args: argparse.Namespace, stdin_lines=None):
    """Run split and capture stdout."""
    buf = io.StringIO()
    stdin = io.StringIO("".join(stdin_lines or []))
    with patch("sys.stdout", buf), patch("sys.stdin", stdin):
        rc = run_split(args)
    return rc, buf.getvalue()


class TestBuildSplitParser:
    def test_returns_parser(self):
        p = build_split_parser()
        assert isinstance(p, argparse.ArgumentParser)

    def test_defaults(self):
        p = build_split_parser()
        ns = p.parse_args([])
        assert ns.output_dir == "."
        assert ns.prefix == "split"
        assert ns.suffix == ".log"
        assert ns.field is None
        assert ns.pattern is None

    def test_field_and_pattern_mutually_exclusive(self):
        p = build_split_parser()
        with pytest.raises(SystemExit):
            p.parse_args(["-f", "level", "-e", "(ERROR)"])


def test_invalid_pattern_returns_error():
    args = _ns(pattern="[invalid")
    rc, _ = _run(args, stdin_lines=[])
    assert rc == 1


def test_stdin_split_by_field(tmp_path):
    lines = ['{"level":"info","msg":"a"}\n', '{"level":"error","msg":"b"}\n']
    args = _ns(output_dir=str(tmp_path), field="level")
    rc, out = _run(args, stdin_lines=lines)
    assert rc == 0
    assert "info" in out
    assert "error" in out


def test_file_split(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("level=debug msg=x\nlevel=info msg=y\n")
    out_dir = tmp_path / "out"
    args = _ns(file=str(log), output_dir=str(out_dir), field="level")
    rc, out = _run(args)
    assert rc == 0
    assert os.path.isdir(out_dir)


def test_output_shows_counts(tmp_path):
    lines = ["level=warn msg=1\n", "level=warn msg=2\n"]
    args = _ns(output_dir=str(tmp_path), field="level")
    rc, out = _run(args, stdin_lines=lines)
    assert "2 line(s)" in out
