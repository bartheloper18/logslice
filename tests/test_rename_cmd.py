"""Tests for logslice.rename_cmd."""

from __future__ import annotations

import argparse
import io
import json

import pytest

from logslice.rename_cmd import build_rename_parser, run_rename


def _ns(**kwargs) -> argparse.Namespace:
    defaults = dict(mapping=["msg=message"], file=None, output=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(ns, stdin_lines=None):
    out = io.StringIO()
    if stdin_lines is not None:
        import logslice.rename_cmd as mod
        import unittest.mock as mock
        fake_stdin = io.StringIO("".join(stdin_lines))
        with mock.patch("logslice.rename_cmd.sys.stdin", fake_stdin):
            rc = run_rename(ns, out)
    else:
        rc = run_rename(ns, out)
    out.seek(0)
    return rc, out.read()


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class TestBuildRenameParser:
    def test_returns_parser(self):
        p = build_rename_parser()
        assert isinstance(p, argparse.ArgumentParser)

    def test_mapping_positional(self):
        p = build_rename_parser()
        ns = p.parse_args(["msg=message"])
        assert ns.mapping == ["msg=message"]

    def test_multiple_mappings(self):
        p = build_rename_parser()
        ns = p.parse_args(["msg=message", "lvl=level"])
        assert len(ns.mapping) == 2

    def test_defaults(self):
        p = build_rename_parser()
        ns = p.parse_args(["a=b"])
        assert ns.file is None
        assert ns.output is None


# ---------------------------------------------------------------------------
# run_rename
# ---------------------------------------------------------------------------

def test_invalid_mapping_returns_error():
    ns = _ns(mapping=["badmapping"])
    rc, _ = _run(ns, stdin_lines=[])
    assert rc == 1


def test_empty_sides_returns_error():
    ns = _ns(mapping=["=new"])
    rc, _ = _run(ns, stdin_lines=[])
    assert rc == 1


def test_rename_from_stdin():
    lines = ['{"msg":"hello","level":"info"}\n']
    ns = _ns(mapping=["msg=message"])
    rc, output = _run(ns, stdin_lines=lines)
    assert rc == 0
    obj = json.loads(output.strip())
    assert "message" in obj
    assert "msg" not in obj


def test_rename_from_file(tmp_path):
    f = tmp_path / "log.jsonl"
    f.write_text('{"a":1}\n{"a":2}\n')
    ns = _ns(mapping=["a=alpha"], file=str(f))
    rc, output = _run(ns)
    assert rc == 0
    lines = [json.loads(l) for l in output.strip().splitlines()]
    assert all("alpha" in obj for obj in lines)
    assert all("a" not in obj for obj in lines)


def test_rename_to_output_file(tmp_path):
    src = tmp_path / "in.jsonl"
    dst = tmp_path / "out.jsonl"
    src.write_text('{"x":1}\n')
    ns = _ns(mapping=["x=y"], file=str(src), output=str(dst))
    rc, _ = _run(ns)
    assert rc == 0
    obj = json.loads(dst.read_text().strip())
    assert obj == {"y": 1}
