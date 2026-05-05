"""Tests for logslice.tail_cmd."""

import io

import pytest

from logslice.tail_cmd import run_tail


def _make_log(tmp_path, n=20):
    p = tmp_path / "app.log"
    p.write_text("".join(f"2024-01-01 00:00:{i:02d} INFO line {i}\n" for i in range(n)))
    return str(p)


class TestRunTail:
    def test_default_shows_last_10(self, tmp_path):
        path = _make_log(tmp_path, 20)
        out = io.StringIO()
        run_tail(path, lines=10, follow=False, color=False, out=out)
        result = out.getvalue().strip().splitlines()
        assert len(result) == 10
        assert "line 19" in result[-1]
        assert "line 10" in result[0]

    def test_lines_param_respected(self, tmp_path):
        path = _make_log(tmp_path, 20)
        out = io.StringIO()
        run_tail(path, lines=3, follow=False, color=False, out=out)
        result = out.getvalue().strip().splitlines()
        assert len(result) == 3

    def test_fewer_lines_than_requested(self, tmp_path):
        path = _make_log(tmp_path, 5)
        out = io.StringIO()
        run_tail(path, lines=10, follow=False, color=False, out=out)
        result = out.getvalue().strip().splitlines()
        assert len(result) == 5

    def test_color_flag_does_not_crash(self, tmp_path):
        path = _make_log(tmp_path, 5)
        out = io.StringIO()
        run_tail(path, lines=5, follow=False, color=True, out=out)
        assert out.getvalue()  # something was written

    def test_no_follow_returns_immediately(self, tmp_path):
        """run_tail should return without blocking when follow=False."""
        path = _make_log(tmp_path, 5)
        out = io.StringIO()
        # If this hangs the test suite will time-out — that's the assertion.
        run_tail(path, lines=5, follow=False, color=False, out=out)
        assert True

    def test_output_lines_end_with_newline(self, tmp_path):
        path = _make_log(tmp_path, 3)
        out = io.StringIO()
        run_tail(path, lines=3, follow=False, color=False, out=out)
        for line in out.getvalue().splitlines(keepends=True):
            assert line.endswith("\n")
