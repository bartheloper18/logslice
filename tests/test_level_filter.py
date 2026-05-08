"""Tests for logslice.level_filter and logslice.level_cmd."""

from __future__ import annotations

import argparse
import io
from typing import List

import pytest

from logslice.level_filter import (
    canonicalize,
    extract_level,
    filter_by_level,
    severity,
)
from logslice.level_cmd import build_level_parser, run_level


# ---------------------------------------------------------------------------
# canonicalize
# ---------------------------------------------------------------------------

def test_canonicalize_info():
    assert canonicalize("info") == "info"


def test_canonicalize_warn_alias():
    assert canonicalize("warn") == "warning"


def test_canonicalize_crit_alias():
    assert canonicalize("crit") == "critical"


def test_canonicalize_unknown_returns_none():
    assert canonicalize("verbose") is None


def test_canonicalize_case_insensitive():
    assert canonicalize("ERROR") == "error"


# ---------------------------------------------------------------------------
# severity ordering
# ---------------------------------------------------------------------------

def test_severity_debug_less_than_error():
    assert severity("debug") < severity("error")


def test_severity_fatal_highest():
    assert severity("fatal") > severity("critical")


def test_severity_unknown_returns_minus_one():
    assert severity("trace") == -1


# ---------------------------------------------------------------------------
# extract_level
# ---------------------------------------------------------------------------

def test_extract_level_from_bracket():
    assert extract_level("2024-01-01 [ERROR] something failed") == "error"


def test_extract_level_warn_alias_canonicalized():
    assert extract_level("WARN: disk almost full") == "warning"


def test_extract_level_no_level_returns_none():
    assert extract_level("nothing interesting here") is None


def test_extract_level_case_insensitive():
    assert extract_level("level=Info msg=started") == "info"


# ---------------------------------------------------------------------------
# filter_by_level
# ---------------------------------------------------------------------------

LINES: List[str] = [
    "2024-01-01 DEBUG initialising\n",
    "2024-01-01 INFO  service started\n",
    "2024-01-01 WARNING disk usage high\n",
    "2024-01-01 ERROR  connection refused\n",
    "2024-01-01 FATAL  out of memory\n",
    "no level here\n",
]


def test_min_info_excludes_debug():
    result = list(filter_by_level(LINES, "info"))
    assert not any("DEBUG" in l for l in result)
    assert any("INFO" in l for l in result)


def test_min_error_only_error_and_above():
    result = list(filter_by_level(LINES, "error"))
    assert len(result) == 2


def test_max_level_caps_output():
    result = list(filter_by_level(LINES, "info", max_level="warning"))
    assert len(result) == 2
    assert all(any(kw in l for kw in ("INFO", "WARNING")) for l in result)


def test_lines_without_level_dropped():
    result = list(filter_by_level(LINES, "debug"))
    assert not any("no level" in l for l in result)


# ---------------------------------------------------------------------------
# CLI run_level
# ---------------------------------------------------------------------------

def _run(min_level: str, lines: List[str], max_level=None) -> str:
    ns = argparse.Namespace(min_level=min_level, max_level=max_level, files=[], output=None)
    buf = io.StringIO()
    import unittest.mock as mock
    with mock.patch("sys.stdin", io.StringIO("".join(lines))):
        run_level(ns, out=buf)
    return buf.getvalue()


def test_cli_filters_below_min():
    out = _run("error", LINES)
    assert "DEBUG" not in out
    assert "ERROR" in out


def test_cli_with_max_level():
    out = _run("info", LINES, max_level="warning")
    assert "FATAL" not in out
    assert "WARNING" in out


def test_build_level_parser_returns_parser():
    p = build_level_parser()
    assert isinstance(p, argparse.ArgumentParser)
