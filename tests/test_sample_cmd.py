"""Tests for logslice.sample_cmd."""

from __future__ import annotations

import argparse
import io
import textwrap

import pytest

from logslice.sample_cmd import build_sample_parser, run_sample


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(file=None, every=None, fraction=None, seed=None)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


LINES = "".join(f"line {i}\n" for i in range(1, 11))


class TestRunSample:
    def test_every_from_stdin(self, tmp_path, monkeypatch):
        import logslice.sample_cmd as mod
        monkeypatch.setattr(mod, "sys", __import__("sys"))
        import sys
        monkeypatch.setattr(sys, "stdin", io.StringIO(LINES))
        out = io.StringIO()
        args = _make_args(every=2)
        rc = run_sample(args, out=out)
        assert rc == 0
        assert out.getvalue() == "line 2\nline 4\nline 6\nline 8\nline 10\n"

    def test_every_from_file(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text(LINES)
        out = io.StringIO()
        args = _make_args(file=str(log), every=5)
        rc = run_sample(args, out=out)
        assert rc == 0
        assert out.getvalue() == "line 5\nline 10\n"

    def test_fraction_1_keeps_all(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text(LINES)
        out = io.StringIO()
        args = _make_args(file=str(log), fraction=1.0, seed=0)
        rc = run_sample(args, out=out)
        assert rc == 0
        assert out.getvalue() == LINES

    def test_missing_file_returns_error(self):
        out = io.StringIO()
        args = _make_args(file="/no/such/file.log", every=1)
        rc = run_sample(args, out=out)
        assert rc == 1

    def test_invalid_every_returns_error(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text(LINES)
        out = io.StringIO()
        args = _make_args(file=str(log), every=-3)
        rc = run_sample(args, out=out)
        assert rc == 1


class TestBuildSampleParser:
    def _parser(self):
        p = argparse.ArgumentParser()
        sub = p.add_subparsers(dest="cmd")
        build_sample_parser(sub)
        return p

    def test_every_parsed(self):
        p = self._parser()
        args = p.parse_args(["sample", "--every", "3"])
        assert args.every == 3

    def test_fraction_parsed(self):
        p = self._parser()
        args = p.parse_args(["sample", "--fraction", "0.25"])
        assert args.fraction == pytest.approx(0.25)

    def test_seed_parsed(self):
        p = self._parser()
        args = p.parse_args(["sample", "--fraction", "0.5", "--seed", "7"])
        assert args.seed == 7
