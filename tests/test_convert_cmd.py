"""Tests for logslice.convert_cmd."""
from __future__ import annotations

import argparse
import io
import json

import pytest

from logslice.convert_cmd import build_convert_parser, run_convert


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"target": "json", "file": None, "output": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(ns, input_lines=None):
    out = io.StringIO()
    if input_lines is not None:
        import unittest.mock as mock
        import sys
        fake_stdin = io.StringIO("".join(input_lines))
        with mock.patch("sys.stdin", fake_stdin):
            code = run_convert(ns, out)
    else:
        code = run_convert(ns, out)
    return code, out.getvalue()


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def test_returns_parser():
    p = build_convert_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_target_required():
    p = build_convert_parser()
    with pytest.raises(SystemExit):
        p.parse_args([])


def test_valid_targets():
    p = build_convert_parser()
    for t in ("json", "kv", "plain"):
        ns = p.parse_args([t])
        assert ns.target == t


def test_invalid_target_exits():
    p = build_convert_parser()
    with pytest.raises(SystemExit):
        p.parse_args(["xml"])


# ---------------------------------------------------------------------------
# run_convert — stdin
# ---------------------------------------------------------------------------

def test_kv_from_stdin_to_json():
    ns = _ns(target="json", file=None)
    code, output = _run(ns, input_lines=["level=INFO msg=hello\n"])
    assert code == 0
    obj = json.loads(output.strip())
    assert obj["level"] == "INFO"


def test_json_from_stdin_to_kv():
    ns = _ns(target="kv", file=None)
    line = json.dumps({"x": "1"}) + "\n"
    code, output = _run(ns, input_lines=[line])
    assert code == 0
    assert "x=1" in output


# ---------------------------------------------------------------------------
# run_convert — file input
# ---------------------------------------------------------------------------

def test_json_file_to_plain(tmp_path):
    src = tmp_path / "a.log"
    src.write_text(json.dumps({"level": "DEBUG", "msg": "test"}) + "\n")
    ns = _ns(target="plain", file=str(src))
    out = io.StringIO()
    code = run_convert(ns, out)
    assert code == 0
    text = out.getvalue()
    assert "DEBUG" in text or "test" in text


def test_output_written_to_file(tmp_path):
    src = tmp_path / "b.log"
    dest = tmp_path / "out.log"
    src.write_text("key=val\n")
    ns = _ns(target="json", file=str(src), output=str(dest))
    out = io.StringIO()
    code = run_convert(ns, out)
    assert code == 0
    written = dest.read_text()
    assert "key" in written
