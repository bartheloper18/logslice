"""Tests for logslice.output module."""

import io
import pytest
from logslice.output import format_line, write_output


SAMPLE_LINES = [
    "2024-01-15T10:00:00 INFO service started\n",
    "2024-01-15T10:01:00 DEBUG processing request\n",
    "2024-01-15T10:02:00 ERROR connection refused\n",
]


class TestFormatLine:
    def test_no_color_no_number(self):
        result = format_line("2024-01-01 INFO hello", use_color=False)
        assert result == "2024-01-01 INFO hello"

    def test_with_line_number(self):
        result = format_line("2024-01-01 INFO hello", use_color=False,
                             show_line_numbers=True, line_number=42)
        assert "42" in result
        assert "INFO hello" in result

    def test_strips_trailing_newline(self):
        result = format_line("2024-01-01 INFO hello\n", use_color=False)
        assert not result.endswith("\n")


class TestWriteOutput:
    def test_writes_all_lines(self):
        buf = io.StringIO()
        count = write_output(SAMPLE_LINES, output=buf, use_color=False)
        assert count == 3
        output = buf.getvalue()
        assert "INFO service started" in output
        assert "ERROR connection refused" in output

    def test_count_only_mode(self):
        buf = io.StringIO()
        count = write_output(SAMPLE_LINES, output=buf, use_color=False, count_only=True)
        assert count == 3
        assert buf.getvalue().strip() == "3"

    def test_line_numbers_in_output(self):
        buf = io.StringIO()
        write_output(SAMPLE_LINES, output=buf, use_color=False, show_line_numbers=True)
        lines = buf.getvalue().splitlines()
        assert lines[0].lstrip().startswith("1:")
        assert lines[2].lstrip().startswith("3:")

    def test_empty_input(self):
        buf = io.StringIO()
        count = write_output([], output=buf, use_color=False)
        assert count == 0
        assert buf.getvalue() == ""

    def test_returns_correct_count(self):
        buf = io.StringIO()
        count = write_output(iter(SAMPLE_LINES), output=buf, use_color=False)
        assert count == len(SAMPLE_LINES)
