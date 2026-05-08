"""Tests for logslice.rate."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logslice.rate import _floor_to_window, bucket_lines, format_rate, iter_rate


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _dt(ts: str) -> datetime:
    """Parse an ISO-8601 string with UTC timezone."""
    return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)


_LINES = [
    "2024-01-01T00:00:05Z INFO  starting up\n",
    "2024-01-01T00:00:30Z INFO  ready\n",
    "2024-01-01T00:01:10Z ERROR something failed\n",
    "2024-01-01T00:01:55Z WARN  retrying\n",
    "2024-01-01T00:03:01Z INFO  recovered\n",
    "no timestamp here — should be ignored\n",
]


# ---------------------------------------------------------------------------
# _floor_to_window
# ---------------------------------------------------------------------------

class TestFloorToWindow:
    def test_already_on_boundary(self):
        dt = _dt("2024-01-01T00:01:00")
        assert _floor_to_window(dt, 60) == dt

    def test_mid_window(self):
        dt = _dt("2024-01-01T00:01:45")
        expected = _dt("2024-01-01T00:01:00")
        assert _floor_to_window(dt, 60) == expected

    def test_five_second_window(self):
        dt = _dt("2024-01-01T00:00:13")
        expected = _dt("2024-01-01T00:00:10")
        assert _floor_to_window(dt, 5) == expected


# ---------------------------------------------------------------------------
# bucket_lines
# ---------------------------------------------------------------------------

class TestBucketLines:
    def test_returns_dict(self):
        result = bucket_lines(_LINES, window_seconds=60)
        assert isinstance(result, dict)

    def test_ignores_non_timestamped(self):
        result = bucket_lines(["no timestamp\n"], window_seconds=60)
        assert result == {}

    def test_correct_bucket_count(self):
        result = bucket_lines(_LINES, window_seconds=60)
        # minute 0 → 2 events, minute 1 → 2 events, minute 3 → 1 event
        assert len(result) == 3

    def test_counts_per_bucket(self):
        result = bucket_lines(_LINES, window_seconds=60)
        counts = list(result.values())
        assert counts == [2, 2, 1]

    def test_sorted_by_time(self):
        result = bucket_lines(_LINES, window_seconds=60)
        keys = list(result.keys())
        assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# iter_rate
# ---------------------------------------------------------------------------

def test_iter_rate_yields_tuples():
    pairs = list(iter_rate(_LINES, window_seconds=60))
    assert all(isinstance(dt, datetime) and isinstance(n, int) for dt, n in pairs)


def test_iter_rate_length_matches_bucket_lines():
    buckets = bucket_lines(_LINES, window_seconds=60)
    pairs = list(iter_rate(_LINES, window_seconds=60))
    assert len(pairs) == len(buckets)


# ---------------------------------------------------------------------------
# format_rate
# ---------------------------------------------------------------------------

def test_format_rate_returns_list_of_strings():
    buckets = bucket_lines(_LINES, window_seconds=60)
    rows = format_rate(buckets, window_seconds=60)
    assert isinstance(rows, list)
    assert all(isinstance(r, str) for r in rows)


def test_format_rate_contains_count():
    buckets = bucket_lines(_LINES, window_seconds=60)
    rows = format_rate(buckets, window_seconds=60)
    assert any("2" in row for row in rows)


def test_format_rate_contains_rate():
    buckets = bucket_lines(_LINES, window_seconds=60)
    rows = format_rate(buckets, window_seconds=60)
    # rate string should contain a slash
    assert any("/s" in row for row in rows)


def test_format_rate_custom_label():
    buckets = bucket_lines(_LINES, window_seconds=60)
    rows = format_rate(buckets, window_seconds=60, label="requests")
    assert any("requests" in row for row in rows)


def test_format_rate_empty_buckets():
    assert format_rate({}) == []
