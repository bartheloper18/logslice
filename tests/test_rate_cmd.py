"""Tests for logslice.rate_cmd."""

from __future__ import annotations

import argparse
import io
import os
import tempfile

import pytest

from logslice.rate_cmd import build_rate_parser, run_rate


_LOG_LINES = (
    "2024-01-01T00:00:05Z INFO  a\n"
    "2024-01-01T00:00:40Z INFO  b\n"
    "2024-01-01T00:01:15Z ERROR c\n"
)


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"file": None, "window": 60, "label": "events"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(args: argparse.Namespace) -> str:
    out = io.StringIO()
    run_rate(args, out=out)
    return out.getvalue()


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------

class TestBuildRateParser:
    def test_returns_parser(self):
        assert isinstance(build_rate_parser(), argparse.ArgumentParser)

    def test_defaults(self):
        parser = build_rate_parser()
        args = parser.parse_args([])
        assert args.window == 60
        assert args.label == "events"
        assert args.file is None

    def test_window_flag(self):
        parser = build_rate_parser()
        args = parser.parse_args(["-w", "30"])
        assert args.window == 30


# ---------------------------------------------------------------------------
# run_rate
# ---------------------------------------------------------------------------

class TestRunRate:
    def test_invalid_window_returns_error(self):
        out = io.StringIO()
        rc = run_rate(_ns(window=0), out=out)
        assert rc == 1
        assert "error" in out.getvalue()

    def test_missing_file_returns_error(self):
        out = io.StringIO()
        rc = run_rate(_ns(file="/no/such/file.log"), out=out)
        assert rc == 1
        assert "error" in out.getvalue()

    def test_no_timestamps_prints_notice(self, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("no timestamps here\n"))
        out = io.StringIO()
        rc = run_rate(_ns(), out=out)
        assert rc == 0
        assert "no timestamped" in out.getvalue()

    def test_from_file(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text(_LOG_LINES)
        out = io.StringIO()
        rc = run_rate(_ns(file=str(log)), out=out)
        assert rc == 0
        output = out.getvalue()
        assert "/s" in output
        assert "events" in output

    def test_custom_label_in_output(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text(_LOG_LINES)
        out = io.StringIO()
        rc = run_rate(_ns(file=str(log), label="hits"), out=out)
        assert rc == 0
        assert "hits" in out.getvalue()

    def test_two_buckets_two_rows(self, tmp_path):
        log = tmp_path / "app.log"
        log.write_text(_LOG_LINES)
        out = io.StringIO()
        run_rate(_ns(file=str(log), window=60), out=out)
        rows = [r for r in out.getvalue().splitlines() if r.strip()]
        assert len(rows) == 2
