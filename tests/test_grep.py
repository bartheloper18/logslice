"""Tests for logslice.grep module."""

import re
import pytest
from logslice.grep import (
    compile_pattern,
    grep_lines,
    grep_file,
    count_matches,
)


SAMPLE_LINES = [
    "2024-01-01T10:00:00 INFO  Service started",
    "2024-01-01T10:01:00 ERROR Failed to connect",
    "2024-01-01T10:02:00 INFO  Retrying connection",
    "2024-01-01T10:03:00 WARN  Slow response detected",
    "2024-01-01T10:04:00 ERROR Timeout after 30s",
]


class TestCompilePattern:
    def test_basic_pattern(self):
        pat = compile_pattern("ERROR")
        assert pat.search("ERROR something") is not None

    def test_ignore_case(self):
        pat = compile_pattern("error", ignore_case=True)
        assert pat.search("ERROR something") is not None

    def test_case_sensitive_no_match(self):
        pat = compile_pattern("error", ignore_case=False)
        assert pat.search("ERROR something") is None

    def test_fixed_string_escapes_regex(self):
        pat = compile_pattern("1.0.0", fixed_string=True)
        # Should match literal dots, not regex any-char
        assert pat.search("v1.0.0") is not None
        assert pat.search("v1X0Y0") is None

    def test_regex_pattern(self):
        pat = compile_pattern(r"ERROR|WARN")
        assert pat.search("WARN slow") is not None
        assert pat.search("INFO ok") is None


class TestGrepLines:
    def test_filter_errors(self):
        pat = compile_pattern("ERROR")
        results = list(grep_lines(SAMPLE_LINES, pat))
        assert len(results) == 2
        assert all("ERROR" in r for r in results)

    def test_invert_match(self):
        pat = compile_pattern("ERROR")
        results = list(grep_lines(SAMPLE_LINES, pat, invert=True))
        assert len(results) == 3
        assert all("ERROR" not in r for r in results)

    def test_no_matches_returns_empty(self):
        pat = compile_pattern("CRITICAL")
        results = list(grep_lines(SAMPLE_LINES, pat))
        assert results == []

    def test_all_match_invert_empty(self):
        pat = compile_pattern("2024")
        results = list(grep_lines(SAMPLE_LINES, pat, invert=True))
        assert results == []

    def test_empty_input(self):
        pat = compile_pattern("ERROR")
        assert list(grep_lines([], pat)) == []


class TestCountMatches:
    def test_count_errors(self):
        pat = compile_pattern("ERROR")
        assert count_matches(SAMPLE_LINES, pat) == 2

    def test_count_inverted(self):
        pat = compile_pattern("ERROR")
        assert count_matches(SAMPLE_LINES, pat, invert=True) == 3

    def test_count_no_match(self):
        pat = compile_pattern("CRITICAL")
        assert count_matches(SAMPLE_LINES, pat) == 0


class TestGrepFile:
    def test_grep_file(self, tmp_path):
        log_file = tmp_path / "app.log"
        log_file.write_text("\n".join(SAMPLE_LINES) + "\n", encoding="utf-8")
        pat = compile_pattern("ERROR")
        results = list(grep_file(str(log_file), pat))
        assert len(results) == 2

    def test_grep_file_invert(self, tmp_path):
        log_file = tmp_path / "app.log"
        log_file.write_text("\n".join(SAMPLE_LINES) + "\n", encoding="utf-8")
        pat = compile_pattern("ERROR")
        results = list(grep_file(str(log_file), pat, invert=True))
        assert len(results) == 3
