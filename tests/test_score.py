"""Tests for logslice.score and logslice.score_cmd."""
from __future__ import annotations

import argparse
import io
import sys

import pytest

from logslice.score import (
    ScoredLine,
    compile_weights,
    format_scored,
    score_line,
    score_lines,
)
from logslice.score_cmd import build_score_parser, run_score


# ---------------------------------------------------------------------------
# score_line
# ---------------------------------------------------------------------------

def test_score_line_single_match():
    compiled = compile_weights({"error": 3.0})
    score, matched = score_line("2024-01-01 ERROR something bad", compiled)
    assert score == 3.0
    assert "error" in matched


def test_score_line_no_match():
    compiled = compile_weights({"error": 3.0})
    score, matched = score_line("INFO all good", compiled)
    assert score == 0.0
    assert matched == []


def test_score_line_multiple_patterns():
    compiled = compile_weights({"error": 2.0, "timeout": 1.5})
    score, matched = score_line("ERROR timeout exceeded", compiled)
    assert score == pytest.approx(3.5)
    assert len(matched) == 2


def test_score_line_case_insensitive():
    compiled = compile_weights({"CRITICAL": 5.0})
    score, _ = score_line("critical failure", compiled)
    assert score == 5.0


# ---------------------------------------------------------------------------
# score_lines
# ---------------------------------------------------------------------------

def test_score_lines_threshold_filters():
    lines = ["ERROR bad\n", "INFO ok\n", "WARN slow\n"]
    weights = {"error": 3.0, "warn": 1.0}
    results = score_lines(lines, weights, threshold=2.0)
    assert len(results) == 1
    assert results[0].score == 3.0


def test_score_lines_sorted_descending():
    lines = ["warn minor\n", "error critical\n", "info nothing\n"]
    weights = {"warn": 1.0, "error": 5.0}
    results = score_lines(lines, weights, threshold=0.0)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_score_lines_top_n():
    lines = [f"error {i}\n" for i in range(10)]
    weights = {"error": 1.0}
    results = score_lines(lines, weights, top_n=3)
    assert len(results) == 3


def test_score_lines_lineno_correct():
    lines = ["ok\n", "error here\n", "fine\n"]
    weights = {"error": 1.0}
    results = score_lines(lines, weights, threshold=0.5)
    assert results[0].lineno == 2


def test_score_lines_empty_input():
    assert score_lines([], {"error": 1.0}) == []


# ---------------------------------------------------------------------------
# format_scored
# ---------------------------------------------------------------------------

def test_format_scored_includes_score_and_lineno():
    sl = ScoredLine(lineno=42, text="error happened\n", score=3.5, matched=["error"])
    out = format_scored(sl)
    assert "42" in out
    assert "3.50" in out
    assert "error happened" in out


def test_format_scored_suppress_score():
    sl = ScoredLine(lineno=1, text="line\n", score=1.0)
    out = format_scored(sl, show_score=False)
    assert "1.00" not in out


def test_format_scored_suppress_lineno():
    sl = ScoredLine(lineno=7, text="line\n", score=1.0)
    out = format_scored(sl, show_lineno=False)
    assert "7" not in out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    defaults = dict(
        weights=["error:2.0"],
        file=None,
        threshold=0.0,
        top=None,
        no_score=False,
        no_lineno=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_run_score_basic(capsys):
    out = io.StringIO()
    ns = _ns(weights=["error:3.0"])
    # Provide lines via stdin mock
    original_stdin = sys.stdin
    sys.stdin = io.StringIO("ERROR bad thing happened\nINFO all good\n")
    try:
        rc = run_score(ns, out=out)
    finally:
        sys.stdin = original_stdin
    assert rc == 0
    result = out.getvalue()
    assert "ERROR bad thing happened" in result
    assert "INFO all good" not in result


def test_run_score_bad_weight_returns_1():
    out = io.StringIO()
    ns = _ns(weights=["errorNOWEIGHT"])
    rc = run_score(ns, out=out)
    assert rc == 1


def test_run_score_missing_file_returns_1():
    out = io.StringIO()
    ns = _ns(weights=["error:1.0"], file="/nonexistent/path/file.log")
    rc = run_score(ns, out=out)
    assert rc == 1


def test_build_score_parser_returns_parser():
    p = build_score_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_build_score_parser_defaults():
    p = build_score_parser()
    ns = p.parse_args(["error:1.0"])
    assert ns.threshold == 0.0
    assert ns.top is None
    assert ns.no_score is False
    assert ns.no_lineno is False
