"""Tests for logslice.chunk_cmd."""

from __future__ import annotations

import argparse
import io

import pytest

from logslice.chunk_cmd import build_chunk_parser, run_chunk


def _ns(**kwargs) -> argparse.Namespace:
    defaults = dict(file="-", size=None, seconds=None, prefix="chunk")
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(args: argparse.Namespace, stdin_lines=None):
    out = io.StringIO()
    if stdin_lines is not None:
        import unittest.mock as mock
        import sys
        with mock.patch("sys.stdin", io.StringIO("".join(stdin_lines))):
            rc = run_chunk(args, out=out)
    else:
        rc = run_chunk(args, out=out)
    return rc, out.getvalue()


class TestBuildChunkParser:
    def test_returns_parser(self):
        sub = argparse.ArgumentParser().add_subparsers()
        p = build_chunk_parser(sub)
        assert isinstance(p, argparse.ArgumentParser)

    def test_defaults(self):
        sub = argparse.ArgumentParser().add_subparsers()
        build_chunk_parser(sub)


class TestRunChunk:
    def test_count_from_stdin(self):
        lines = [f"line {i}\n" for i in range(4)]
        rc, out = _run(_ns(size=2), stdin_lines=lines)
        assert rc == 0
        assert "--- chunk 1 ---" in out
        assert "--- chunk 2 ---" in out

    def test_prefix_respected(self):
        lines = ["a\n", "b\n"]
        rc, out = _run(_ns(size=2, prefix="seg"), stdin_lines=lines)
        assert "--- seg 1 ---" in out

    def test_count_from_file(self, tmp_path):
        f = tmp_path / "log.txt"
        f.write_text("".join(f"line {i}\n" for i in range(6)))
        rc, out = _run(_ns(file=str(f), size=3))
        assert rc == 0
        assert out.count("--- chunk") == 2

    def test_seconds_from_file(self, tmp_path):
        f = tmp_path / "log.txt"
        content = (
            "2024-01-01T00:00:00Z a\n"
            "2024-01-01T00:00:05Z b\n"
            "2024-01-01T00:00:15Z c\n"
        )
        f.write_text(content)
        rc, out = _run(_ns(file=str(f), seconds=10.0))
        assert rc == 0
        assert out.count("--- chunk") == 2

    def test_missing_file_returns_1(self):
        rc, out = _run(_ns(file="/nonexistent/file.log", size=10))
        assert rc == 1
