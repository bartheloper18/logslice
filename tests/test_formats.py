"""Tests for logslice.formats and logslice.detector modules."""

import pytest
from logslice.formats import detect_format, list_formats, FORMATS
from logslice.detector import detect_format_from_lines, detect_format_from_file


# ---------------------------------------------------------------------------
# detect_format tests
# ---------------------------------------------------------------------------

class TestDetectFormat:
    def test_iso8601_with_T(self):
        line = "2024-01-15T12:30:45Z INFO service started"
        fmt = detect_format(line)
        assert fmt is not None
        assert fmt.name == "iso8601"

    def test_iso8601_space_separator(self):
        line = "2024-01-15 12:30:45.123 ERROR something failed"
        fmt = detect_format(line)
        assert fmt is not None
        assert fmt.name == "iso8601"

    def test_apache_format(self):
        line = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'
        fmt = detect_format(line)
        assert fmt is not None
        assert fmt.name == "apache"

    def test_syslog_format(self):
        line = "Jan 15 12:00:00 hostname sshd[1234]: Accepted password"
        fmt = detect_format(line)
        assert fmt is not None
        assert fmt.name == "syslog"

    def test_epoch_format(self):
        line = "1705312245 INFO server ready"
        fmt = detect_format(line)
        assert fmt is not None
        assert fmt.name == "epoch"

    def test_no_timestamp_returns_none(self):
        line = "no timestamp here at all"
        fmt = detect_format(line)
        assert fmt is None


# ---------------------------------------------------------------------------
# list_formats tests
# ---------------------------------------------------------------------------

def test_list_formats_returns_all():
    result = list_formats()
    names = [name for name, _ in result]
    assert set(names) == set(FORMATS.keys())


def test_list_formats_has_descriptions():
    for name, description in list_formats():
        assert isinstance(description, str)
        assert len(description) > 0


# ---------------------------------------------------------------------------
# detect_format_from_lines tests
# ---------------------------------------------------------------------------

class TestDetectFormatFromLines:
    def test_majority_iso8601(self):
        lines = [
            "2024-01-15T10:00:00Z DEBUG init",
            "2024-01-15T10:00:01Z INFO started",
            "2024-01-15T10:00:02Z WARN slow query",
            "no timestamp here",
        ]
        fmt = detect_format_from_lines(lines)
        assert fmt is not None
        assert fmt.name == "iso8601"

    def test_empty_lines_returns_none(self):
        assert detect_format_from_lines([]) is None

    def test_blank_lines_ignored(self):
        lines = ["   ", "", "2024-03-01T00:00:00Z INFO ok"]
        fmt = detect_format_from_lines(lines)
        assert fmt is not None
        assert fmt.name == "iso8601"

    def test_all_unrecognised_returns_none(self):
        lines = ["foo bar baz", "hello world", "no dates here"]
        fmt = detect_format_from_lines(lines)
        assert fmt is None


# ---------------------------------------------------------------------------
# detect_format_from_file tests
# ---------------------------------------------------------------------------

def test_detect_format_from_file(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text(
        "2024-06-01T08:00:00Z INFO booting\n"
        "2024-06-01T08:00:01Z DEBUG config loaded\n"
        "2024-06-01T08:00:02Z INFO ready\n"
    )
    fmt = detect_format_from_file(str(log_file))
    assert fmt is not None
    assert fmt.name == "iso8601"


def test_detect_format_from_file_missing_raises(tmp_path):
    with pytest.raises(OSError):
        detect_format_from_file(str(tmp_path / "nonexistent.log"))
