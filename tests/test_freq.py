"""Tests for logslice.freq."""
from __future__ import annotations

import pytest

from logslice.freq import format_freq, freq_lines


# ---------------------------------------------------------------------------
# freq_lines — whole-line mode
# ---------------------------------------------------------------------------

class TestFreqLinesWholeLine:
    def test_empty_input_returns_empty(self):
        assert freq_lines([]) == []

    def test_single_unique_line(self):
        result = freq_lines(["hello\n"])
        assert result == [("hello", 1)]

    def test_duplicate_lines_counted(self):
        lines = ["foo\n", "bar\n", "foo\n", "foo\n"]
        result = freq_lines(lines)
        assert result[0] == ("foo", 3)
        assert result[1] == ("bar", 1)

    def test_sorted_by_descending_count(self):
        lines = ["a\n", "b\n", "b\n", "c\n", "c\n", "c\n"]
        result = freq_lines(lines)
        counts = [c for _, c in result]
        assert counts == sorted(counts, reverse=True)

    def test_top_limits_results(self):
        lines = ["x\n"] * 5 + ["y\n"] * 3 + ["z\n"] * 1
        result = freq_lines(lines, top=2)
        assert len(result) == 2
        assert result[0] == ("x", 5)

    def test_newline_stripped_from_key(self):
        result = freq_lines(["hello\n", "hello\n"])
        assert result[0][0] == "hello"


# ---------------------------------------------------------------------------
# freq_lines — field mode
# ---------------------------------------------------------------------------

class TestFreqLinesField:
    def test_json_field_counted(self):
        lines = [
            '{"level": "INFO"}\n',
            '{"level": "ERROR"}\n',
            '{"level": "INFO"}\n',
        ]
        result = freq_lines(lines, field="level")
        assert result[0] == ("INFO", 2)
        assert result[1] == ("ERROR", 1)

    def test_kv_field_counted(self):
        lines = [
            "status=ok host=web1\n",
            "status=fail host=web2\n",
            "status=ok host=web3\n",
        ]
        result = freq_lines(lines, field="status")
        assert result[0] == ("ok", 2)

    def test_missing_field_skipped(self):
        lines = [
            '{"level": "INFO"}\n',
            '{"msg": "no level here"}\n',
        ]
        result = freq_lines(lines, field="level")
        assert result == [("INFO", 1)]

    def test_plain_lines_skipped_in_field_mode(self):
        lines = ["plain text line\n", "another plain\n"]
        result = freq_lines(lines, field="level")
        assert result == []


# ---------------------------------------------------------------------------
# format_freq
# ---------------------------------------------------------------------------

class TestFormatFreq:
    def test_output_contains_count_and_value(self):
        results = [("foo", 3), ("bar", 1)]
        output = list(format_freq(results, total=4))
        assert any("foo" in line for line in output)
        assert any("3" in line for line in output)

    def test_percentage_calculated(self):
        results = [("x", 1)]
        output = list(format_freq(results, total=2))
        assert "50.0" in output[0]

    def test_zero_total_no_division_error(self):
        results = [("a", 0)]
        output = list(format_freq(results, total=0))
        assert "0.0" in output[0]

    def test_each_result_produces_one_line(self):
        results = [("a", 5), ("b", 3), ("c", 1)]
        output = list(format_freq(results, total=9))
        assert len(output) == 3
