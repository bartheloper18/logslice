"""Tests for logslice.split."""

from __future__ import annotations

import os
import re
import pytest

from logslice.split import _safe_filename, _get_key, split_lines


# ---------------------------------------------------------------------------
# _safe_filename
# ---------------------------------------------------------------------------

def test_safe_filename_plain():
    assert _safe_filename("production") == "production"


def test_safe_filename_spaces_replaced():
    assert _safe_filename("my value") == "my_value"


def test_safe_filename_special_chars():
    result = _safe_filename("a/b:c")
    assert "/" not in result and ":" not in result


def test_safe_filename_empty_returns_unknown():
    assert _safe_filename("") == "unknown"
    assert _safe_filename("   ") == "unknown"


# ---------------------------------------------------------------------------
# _get_key
# ---------------------------------------------------------------------------

def test_get_key_json_field():
    line = '{"level": "error", "msg": "boom"}\n'
    assert _get_key(line, field="level", pattern=None) == "error"


def test_get_key_kv_field():
    line = "level=warn msg=timeout\n"
    assert _get_key(line, field="level", pattern=None) == "warn"


def test_get_key_missing_field_returns_unknown():
    line = "plain text without fields\n"
    assert _get_key(line, field="level", pattern=None) == "unknown"


def test_get_key_pattern_capture_group():
    pat = re.compile(r"(?P<env>prod|staging|dev)")
    assert _get_key("deployed to prod server", field=None, pattern=pat) == "prod"


def test_get_key_pattern_no_match_returns_default():
    pat = re.compile(r"(CRITICAL)")
    assert _get_key("all fine", field=None, pattern=pat) == "default"


def test_get_key_no_field_no_pattern():
    assert _get_key("anything", field=None, pattern=None) == "default"


# ---------------------------------------------------------------------------
# split_lines
# ---------------------------------------------------------------------------

def test_split_creates_files(tmp_path):
    lines = [
        '{"level":"info","msg":"start"}\n',
        '{"level":"error","msg":"boom"}\n',
        '{"level":"info","msg":"end"}\n',
    ]
    counts = split_lines(lines, str(tmp_path), prefix="out", field="level")
    assert counts["info"] == 2
    assert counts["error"] == 1
    assert os.path.exists(tmp_path / "out_info.log")
    assert os.path.exists(tmp_path / "out_error.log")


def test_split_file_contents_correct(tmp_path):
    lines = ["level=warn msg=a\n", "level=info msg=b\n", "level=warn msg=c\n"]
    split_lines(lines, str(tmp_path), field="level")
    warn_path = tmp_path / "split_warn.log"
    content = warn_path.read_text()
    assert "msg=a" in content
    assert "msg=c" in content
    assert "msg=b" not in content


def test_split_pattern_bucket(tmp_path):
    pat = re.compile(r"(ERROR|WARN|INFO)")
    lines = ["INFO service started\n", "ERROR disk full\n", "WARN high memory\n"]
    counts = split_lines(lines, str(tmp_path), pattern=pat)
    assert counts.get("INFO") == 1
    assert counts.get("ERROR") == 1


def test_split_no_trailing_newline_added(tmp_path):
    lines = ["level=info msg=hi"]
    split_lines(lines, str(tmp_path), field="level")
    content = (tmp_path / "split_info.log").read_text()
    assert content.endswith("\n")


def test_split_empty_input_no_files(tmp_path):
    counts = split_lines([], str(tmp_path))
    assert counts == {}
    assert list(tmp_path.iterdir()) == []
