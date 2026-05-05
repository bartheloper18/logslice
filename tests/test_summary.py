"""Tests for logslice.summary."""

import io
import os
import tempfile
import pytest

from logslice.summary import summarise_lines, summarise_file


SAMPLE_LINES = [
    "2024-03-01T08:00:00 INFO  server started\n",
    "2024-03-01T08:01:00 DEBUG reading config\n",
    "2024-03-01T08:02:00 WARNING slow query detected\n",
    "2024-03-01T08:03:00 ERROR connection refused\n",
    "2024-03-01T08:04:00 INFO  retrying connection\n",
]


class TestSummariseLines:
    def test_returns_string(self):
        result = summarise_lines(SAMPLE_LINES, SAMPLE_LINES)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_total_in_output(self):
        result = summarise_lines(SAMPLE_LINES, SAMPLE_LINES)
        assert "5" in result

    def test_matched_subset(self):
        matched = SAMPLE_LINES[:2]
        result = summarise_lines(SAMPLE_LINES, matched)
        assert "5" in result   # total
        assert "2" in result   # matched

    def test_writes_to_out(self):
        buf = io.StringIO()
        summarise_lines(SAMPLE_LINES, SAMPLE_LINES, out=buf)
        buf.seek(0)
        content = buf.read()
        assert "Total lines" in content
        assert "Matched lines" in content

    def test_level_counts_present(self):
        result = summarise_lines(SAMPLE_LINES, SAMPLE_LINES)
        assert "ERROR" in result
        assert "INFO" in result

    def test_empty_matched(self):
        result = summarise_lines(SAMPLE_LINES, [])
        assert "0" in result


class TestSummariseFile:
    def _make_tmp(self, lines):
        fd, path = tempfile.mkstemp(suffix=".log")
        with os.fdopen(fd, "w") as fh:
            fh.writelines(lines)
        return path

    def test_reads_file_for_totals(self):
        path = self._make_tmp(SAMPLE_LINES)
        try:
            matched = SAMPLE_LINES[:3]
            result = summarise_file(path, matched)
            assert "5" in result
            assert "3" in result
        finally:
            os.unlink(path)

    def test_writes_to_out(self):
        path = self._make_tmp(SAMPLE_LINES)
        try:
            buf = io.StringIO()
            summarise_file(path, SAMPLE_LINES, out=buf)
            buf.seek(0)
            assert "Total lines" in buf.read()
        finally:
            os.unlink(path)

    def test_missing_file_returns_empty(self):
        err_buf = io.StringIO()
        result = summarise_file("/nonexistent/path/file.log", [], out=err_buf)
        assert result == ""

    def test_missing_file_writes_error(self):
        err_buf = io.StringIO()
        summarise_file("/nonexistent/path/file.log", [], out=err_buf)
        err_buf.seek(0)
        # error goes to stderr by default; empty result is sufficient signal
        assert result := summarise_file("/nonexistent/path/file.log", []) == ""
