"""Tests for logslice.count."""

from __future__ import annotations

from collections import Counter

import pytest

from logslice.count import (
    count_by_field,
    count_by_pattern,
    format_count,
    count_file,
)


# ---------------------------------------------------------------------------
# count_by_field
# ---------------------------------------------------------------------------

class TestCountByField:
    def test_json_lines(self):
        lines = [
            '{"level": "INFO"}\n',
            '{"level": "ERROR"}\n',
            '{"level": "INFO"}\n',
        ]
        result = count_by_field(lines, "level")
        assert result["INFO"] == 2
        assert result["ERROR"] == 1

    def test_kv_lines(self):
        lines = [
            "level=INFO msg=hello\n",
            "level=DEBUG msg=world\n",
            "level=INFO msg=again\n",
        ]
        result = count_by_field(lines, "level")
        assert result["INFO"] == 2
        assert result["DEBUG"] == 1

    def test_missing_field_skipped(self):
        lines = ['{"other": "x"}\n', '{"level": "WARN"}\n']
        result = count_by_field(lines, "level")
        assert result["WARN"] == 1
        assert sum(result.values()) == 1

    def test_empty_input_returns_empty_counter(self):
        assert count_by_field([], "level") == Counter()

    def test_plain_lines_skipped(self):
        lines = ["no fields here\n", "also plain\n"]
        assert count_by_field(lines, "level") == Counter()


# ---------------------------------------------------------------------------
# count_by_pattern
# ---------------------------------------------------------------------------

class TestCountByPattern:
    def test_full_match_counted(self):
        lines = ["ERROR occurred\n", "ERROR again\n", "INFO ok\n"]
        result = count_by_pattern(lines, r"ERROR|INFO")
        assert result["ERROR"] == 2
        assert result["INFO"] == 1

    def test_capture_group_used(self):
        lines = ["level=INFO\n", "level=ERROR\n", "level=INFO\n"]
        result = count_by_pattern(lines, r"level=(\w+)")
        assert result["INFO"] == 2
        assert result["ERROR"] == 1

    def test_ignore_case(self):
        lines = ["error here\n", "ERROR there\n"]
        result = count_by_pattern(lines, r"error", ignore_case=True)
        assert result["error"] + result.get("ERROR", 0) >= 2 or result.get("error", 0) == 2

    def test_no_match_returns_empty(self):
        lines = ["nothing here\n"]
        assert count_by_pattern(lines, r"NOMATCH") == Counter()


# ---------------------------------------------------------------------------
# format_count
# ---------------------------------------------------------------------------

def test_format_count_sorted_descending():
    counter = Counter({"INFO": 5, "ERROR": 2, "DEBUG": 8})
    lines = list(format_count(counter))
    counts = [int(l.split("\t")[0]) for l in lines]
    assert counts == sorted(counts, reverse=True)


def test_format_count_top_limits_output():
    counter = Counter({"a": 3, "b": 2, "c": 1})
    lines = list(format_count(counter, top=2))
    assert len(lines) == 2


def test_format_count_includes_value_and_count():
    counter = Counter({"INFO": 7})
    line = list(format_count(counter))[0]
    assert "7" in line
    assert "INFO" in line


# ---------------------------------------------------------------------------
# count_file
# ---------------------------------------------------------------------------

def test_count_file_by_field(tmp_path):
    log = tmp_path / "app.log"
    log.write_text(
        '{"level": "INFO"}\n{"level": "ERROR"}\n{"level": "INFO"}\n'
    )
    lines = list(count_file(str(log), field="level"))
    assert any("INFO" in l and "2" in l for l in lines)


def test_count_file_by_pattern(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("ERROR: disk full\nINFO: started\nERROR: timeout\n")
    lines = list(count_file(str(log), pattern=r"ERROR|INFO"))
    assert any("ERROR" in l for l in lines)


def test_count_file_no_field_no_pattern_counts_lines(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("foo\nbar\nfoo\n")
    lines = list(count_file(str(log)))
    assert any("foo" in l and "2" in l for l in lines)
