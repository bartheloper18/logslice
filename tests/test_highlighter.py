"""Tests for logslice.highlighter module."""

import pytest
from logslice.highlighter import (
    highlight_level,
    highlight_timestamp,
    highlight_line,
    ANSI_RED,
    ANSI_GREEN,
    ANSI_YELLOW,
    ANSI_CYAN,
    ANSI_MAGENTA,
    ANSI_BOLD,
    ANSI_RESET,
)


class TestHighlightLevel:
    def test_error_colored_red(self):
        result = highlight_level("2024-01-01 ERROR something failed")
        assert ANSI_RED in result
        assert "ERROR" in result

    def test_info_colored_green(self):
        result = highlight_level("2024-01-01 INFO server started")
        assert ANSI_GREEN in result

    def test_warning_colored_yellow(self):
        result = highlight_level("2024-01-01 WARNING disk space low")
        assert ANSI_YELLOW in result

    def test_warn_colored_yellow(self):
        result = highlight_level("2024-01-01 WARN disk space low")
        assert ANSI_YELLOW in result

    def test_debug_colored_cyan(self):
        result = highlight_level("2024-01-01 DEBUG trace info")
        assert ANSI_CYAN in result

    def test_critical_colored_magenta(self):
        result = highlight_level("2024-01-01 CRITICAL system failure")
        assert ANSI_MAGENTA in result

    def test_no_level_unchanged_structure(self):
        line = "2024-01-01 just a plain log line"
        result = highlight_level(line)
        assert "just a plain log line" in result

    def test_reset_appended(self):
        result = highlight_level("ERROR")
        assert ANSI_RESET in result


class TestHighlightTimestamp:
    def test_timestamp_highlighted(self):
        ts = "2024-01-15T10:30:00"
        line = f"{ts} INFO message"
        result = highlight_timestamp(line, ts)
        assert ANSI_CYAN in result
        assert ts in result

    def test_none_timestamp_unchanged(self):
        line = "no timestamp here"
        result = highlight_timestamp(line, None)
        assert result == line

    def test_missing_timestamp_unchanged(self):
        line = "2024-01-15 INFO message"
        result = highlight_timestamp(line, "9999-99-99")
        assert ANSI_CYAN not in result


class TestHighlightLine:
    def test_no_color_returns_stripped(self):
        line = "2024-01-01 ERROR fail\n"
        result = highlight_line(line, use_color=False)
        assert result == line

    def test_with_color_contains_ansi(self):
        line = "2024-01-01T12:00:00 ERROR something"
        result = highlight_line(line, use_color=True)
        assert ANSI_RESET in result
