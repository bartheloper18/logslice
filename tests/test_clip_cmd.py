"""Tests for logslice.clip_cmd."""
from __future__ import annotations

import io
import argparse

import pytest

from logslice.clip_cmd import build_clip_parser, run_clip


LINES = [f"line {i}\n" for i in range(1, 6)]  # 5 lines


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"start": 1, "end": None, "file": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(ns: argparse.Namespace) -> tuple[int, str]:
    buf = io.StringIO()
    code = run_clip(ns, out=buf)
    return code, buf.getvalue()


class TestBuildClipParser:
    def test_returns_parser(self):
        p = build_clip_parser()
        assert isinstance(p, argparse.ArgumentParser)

    def test_start_required(self):
        p = build_clip_parser()
        with pytest.raises(SystemExit):
            p.parse_args([])

    def test_end_optional(self):
        p = build_clip_parser()
        ns = p.parse_args(["3"])
        assert ns.start == 3
        assert ns.end is None

    def test_start_and_end_parsed(self):
        p = build_clip_parser()
        ns = p.parse_args(["2", "5"])
        assert ns.start == 2
        assert ns.end == 5


class TestRunClip:
    def test_clips_from_file(self, tmp_path):
        p = tmp_path / "a.log"
        p.write_text("".join(LINES))
        code, out = _run(_ns(start=2, end=3, file=str(p)))
        assert code == 0
        assert out == "line 2\nline 3\n"

    def test_open_ended_from_file(self, tmp_path):
        p = tmp_path / "a.log"
        p.write_text("".join(LINES))
        code, out = _run(_ns(start=4, file=str(p)))
        assert code == 0
        assert out == "line 4\nline 5\n"

    def test_invalid_range_returns_error(self, tmp_path):
        p = tmp_path / "a.log"
        p.write_text("".join(LINES))
        code, out = _run(_ns(start=4, end=2, file=str(p)))
        assert code == 1
        assert out == ""

    def test_missing_file_returns_error(self):
        code, out = _run(_ns(start=1, end=2, file="/no/such/file.log"))
        assert code == 1
        assert out == ""

    def test_stdin_mode(self, monkeypatch):
        import sys
        monkeypatch.setattr(sys, "stdin", io.StringIO("".join(LINES)))
        buf = io.StringIO()
        code = run_clip(_ns(start=1, end=2), out=buf)
        assert code == 0
        assert buf.getvalue() == "line 1\nline 2\n"
