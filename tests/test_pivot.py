"""Tests for logslice.pivot and logslice.pivot_cmd."""
from __future__ import annotations

import argparse
import io
import json

import pytest

from logslice.pivot import format_pivot, pivot_lines
from logslice.pivot_cmd import build_pivot_parser, run_pivot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_lines(*records):
    return [json.dumps(r) + "\n" for r in records]


def _kv_lines(*records):
    lines = []
    for rec in records:
        lines.append(" ".join(f"{k}={v}" for k, v in rec.items()) + "\n")
    return lines


# ---------------------------------------------------------------------------
# pivot_lines – JSON input
# ---------------------------------------------------------------------------

class TestPivotLinesJson:
    def test_single_key_counts(self):
        lines = _json_lines(
            {"level": "info"}, {"level": "error"}, {"level": "info"}
        )
        result = pivot_lines(lines, key="level")
        assert result["info"]["count"] == 2
        assert result["error"]["count"] == 1

    def test_missing_key_skipped(self):
        lines = _json_lines({"level": "info"}, {"msg": "no level here"})
        result = pivot_lines(lines, key="level")
        assert list(result.keys()) == ["info"]

    def test_value_aggregation_sum(self):
        lines = _json_lines(
            {"status": "200", "ms": "100"},
            {"status": "200", "ms": "200"},
            {"status": "500", "ms": "50"},
        )
        result = pivot_lines(lines, key="status", value="ms")
        assert result["200"]["sum"] == pytest.approx(300.0)
        assert result["200"]["mean"] == pytest.approx(150.0)
        assert result["500"]["sum"] == pytest.approx(50.0)

    def test_value_field_missing_still_counts(self):
        lines = _json_lines({"status": "200"}, {"status": "200", "ms": "80"})
        result = pivot_lines(lines, key="status", value="ms")
        assert result["200"]["count"] == 2
        assert result["200"]["sum"] == pytest.approx(80.0)

    def test_empty_input_returns_empty(self):
        assert pivot_lines([], key="level") == {}


# ---------------------------------------------------------------------------
# pivot_lines – key=value input
# ---------------------------------------------------------------------------

class TestPivotLinesKv:
    def test_kv_counts(self):
        lines = _kv_lines({"env": "prod"}, {"env": "dev"}, {"env": "prod"})
        result = pivot_lines(lines, key="env")
        assert result["prod"]["count"] == 2
        assert result["dev"]["count"] == 1

    def test_plain_lines_skipped(self):
        lines = ["just a plain log line\n", '{"level": "info"}\n']
        result = pivot_lines(lines, key="level")
        assert list(result.keys()) == ["info"]


# ---------------------------------------------------------------------------
# format_pivot
# ---------------------------------------------------------------------------

class TestFormatPivot:
    def test_empty_data_returns_no_data(self):
        assert "(no data)" in format_pivot({})

    def test_key_and_count_present(self):
        out = format_pivot({"info": {"count": 5}})
        assert "info" in out
        assert "5" in out

    def test_value_columns_shown_when_requested(self):
        data = {"info": {"count": 2, "sum": 300.0, "mean": 150.0}}
        out = format_pivot(data, value="ms")
        assert "SUM" in out
        assert "MEAN" in out
        assert "300.000" in out


# ---------------------------------------------------------------------------
# pivot_cmd
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    defaults = {"key": "level", "value": None, "agg": "count", "file": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestBuildPivotParser:
    def test_returns_parser(self):
        p = build_pivot_parser()
        assert isinstance(p, argparse.ArgumentParser)

    def test_key_positional(self):
        p = build_pivot_parser()
        ns = p.parse_args(["level"])
        assert ns.key == "level"

    def test_value_optional(self):
        p = build_pivot_parser()
        ns = p.parse_args(["level", "--value", "ms"])
        assert ns.value == "ms"


class TestRunPivot:
    def test_reads_stdin(self, monkeypatch):
        lines = _json_lines({"level": "info"}, {"level": "error"})
        monkeypatch.setattr("sys.stdin", io.StringIO("".join(lines)))
        out = io.StringIO()
        rc = run_pivot(_ns(), out=out)
        assert rc == 0
        assert "info" in out.getvalue()

    def test_reads_file(self, tmp_path):
        f = tmp_path / "app.log"
        f.write_text("".join(_json_lines({"level": "warn"}, {"level": "warn"})))
        out = io.StringIO()
        rc = run_pivot(_ns(file=str(f)), out=out)
        assert rc == 0
        assert "2" in out.getvalue()

    def test_missing_file_returns_1(self):
        out = io.StringIO()
        rc = run_pivot(_ns(file="/no/such/file.log"), out=out)
        assert rc == 1
