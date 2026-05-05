"""Tests for logslice.parser and logslice.filter."""

import io
from datetime import datetime

import pytest

from logslice.parser import extract_timestamp, parse_timestamp
from logslice.filter import filter_lines


# ---------------------------------------------------------------------------
# parse_timestamp
# ---------------------------------------------------------------------------

class TestParseTimestamp:
    def test_iso8601_with_millis(self):
        dt = parse_timestamp('2024-01-15T13:45:00.123')
        assert dt == datetime(2024, 1, 15, 13, 45, 0, 123000)

    def test_iso8601_no_millis(self):
        dt = parse_timestamp('2024-01-15T13:45:00')
        assert dt == datetime(2024, 1, 15, 13, 45, 0)

    def test_space_separated(self):
        dt = parse_timestamp('2024-01-15 09:00:00')
        assert dt == datetime(2024, 1, 15, 9, 0, 0)

    def test_apache_format(self):
        dt = parse_timestamp('15/Jan/2024:13:45:00')
        assert dt == datetime(2024, 1, 15, 13, 45, 0)

    def test_invalid_returns_none(self):
        assert parse_timestamp('not-a-date') is None


# ---------------------------------------------------------------------------
# extract_timestamp
# ---------------------------------------------------------------------------

class TestExtractTimestamp:
    def test_json_line_timestamp_key(self):
        line = '{"timestamp": "2024-03-01T10:00:00", "msg": "hello"}'
        dt = extract_timestamp(line)
        assert dt == datetime(2024, 3, 1, 10, 0, 0)

    def test_json_line_ts_key(self):
        line = '{"ts": "2024-03-01 08:30:00", "level": "INFO"}'
        assert extract_timestamp(line) == datetime(2024, 3, 1, 8, 30, 0)

    def test_plain_iso_line(self):
        line = '2024-06-20T22:15:00Z [ERROR] disk full'
        assert extract_timestamp(line) == datetime(2024, 6, 20, 22, 15, 0)

    def test_no_timestamp_returns_none(self):
        assert extract_timestamp('no timestamp here') is None


# ---------------------------------------------------------------------------
# filter_lines
# ---------------------------------------------------------------------------

LOGS = [
    '2024-01-01T08:00:00 startup\n',
    '2024-01-01T09:00:00 checkpoint\n',
    '2024-01-01T10:00:00 warning\n',
    '2024-01-01T11:00:00 shutdown\n',
    'no timestamp line\n',
]


class TestFilterLines:
    def _stream(self):
        return io.StringIO(''.join(LOGS))

    def test_no_bounds_returns_all_parseable(self):
        result = list(filter_lines(self._stream()))
        assert len(result) == 4  # unparseable line excluded by default

    def test_start_bound(self):
        start = datetime(2024, 1, 1, 9, 30, 0)
        result = list(filter_lines(self._stream(), start=start))
        assert all('10:00' in r or '11:00' in r for r in result)
        assert len(result) == 2

    def test_end_bound(self):
        end = datetime(2024, 1, 1, 9, 0, 0)
        result = list(filter_lines(self._stream(), end=end))
        assert len(result) == 2

    def test_start_and_end(self):
        start = datetime(2024, 1, 1, 9, 0, 0)
        end = datetime(2024, 1, 1, 10, 0, 0)
        result = list(filter_lines(self._stream(), start=start, end=end))
        assert len(result) == 2

    def test_include_unparseable(self):
        result = list(filter_lines(self._stream(), include_unparseable=True))
        assert any('no timestamp' in r for r in result)
        assert len(result) == 5
