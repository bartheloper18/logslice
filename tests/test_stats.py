"""Tests for logslice.stats."""

import pytest
from logslice.stats import (
    LogStats,
    extract_level,
    collect_stats,
    format_stats,
)


class TestExtractLevel:
    def test_info(self):
        assert extract_level("2024-01-01 INFO starting up") == "INFO"

    def test_error(self):
        assert extract_level("2024-01-01 ERROR boom") == "ERROR"

    def test_warning_abbrev(self):
        assert extract_level("WARN something odd") == "WARN"

    def test_case_insensitive(self):
        assert extract_level("debug message here") == "DEBUG"

    def test_no_level(self):
        assert extract_level("plain log line without level") is None

    def test_critical(self):
        assert extract_level("[CRITICAL] disk full") == "CRITICAL"


class TestCollectStats:
    def _lines(self):
        return [
            "2024-01-01T10:00:00 INFO  app started",
            "2024-01-01T10:01:00 DEBUG checking config",
            "2024-01-01T10:02:00 ERROR failed to connect",
            "2024-01-01T10:03:00 INFO  retrying",
            "2024-01-01T10:04:00 ERROR timeout",
        ]

    def test_total_and_matched(self):
        all_lines = self._lines()
        matched = all_lines[1:4]
        stats = collect_stats(all_lines, matched)
        assert stats.total_lines == 5
        assert stats.matched_lines == 3

    def test_level_counts(self):
        lines = self._lines()
        stats = collect_stats(lines, lines)
        assert stats.level_counts["INFO"] == 2
        assert stats.level_counts["ERROR"] == 2
        assert stats.level_counts["DEBUG"] == 1

    def test_empty_matched(self):
        stats = collect_stats(self._lines(), [])
        assert stats.matched_lines == 0
        assert stats.level_counts == {}

    def test_timestamps_via_extractor(self):
        from datetime import datetime
        import re
        ts_re = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})')

        def fake_extract(line):
            m = ts_re.search(line)
            if m:
                return datetime.fromisoformat(m.group(1))
            return None

        lines = self._lines()
        stats = collect_stats(lines, lines, extract_ts=fake_extract)
        assert stats.first_timestamp == "2024-01-01 10:00:00"
        assert stats.last_timestamp == "2024-01-01 10:04:00"

    def test_no_extractor_leaves_timestamps_none(self):
        stats = collect_stats(self._lines(), self._lines())
        assert stats.first_timestamp is None
        assert stats.last_timestamp is None


class TestFormatStats:
    def test_contains_totals(self):
        stats = LogStats(total_lines=100, matched_lines=42)
        out = format_stats(stats)
        assert "100" in out
        assert "42" in out

    def test_contains_levels(self):
        from collections import Counter
        stats = LogStats(total_lines=10, matched_lines=10,
                         level_counts=Counter({"ERROR": 3, "INFO": 7}))
        out = format_stats(stats)
        assert "ERROR" in out
        assert "INFO" in out
        assert "3" in out
        assert "7" in out

    def test_no_levels_section_when_empty(self):
        stats = LogStats(total_lines=5, matched_lines=5)
        out = format_stats(stats)
        assert "Level counts" not in out

    def test_timestamps_shown(self):
        stats = LogStats(
            total_lines=2, matched_lines=2,
            first_timestamp="2024-01-01 10:00:00",
            last_timestamp="2024-01-01 10:05:00",
        )
        out = format_stats(stats)
        assert "2024-01-01 10:00:00" in out
        assert "2024-01-01 10:05:00" in out
