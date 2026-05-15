"""Tests for logslice.clip."""
from __future__ import annotations

import pytest

from logslice.clip import clip_lines, clip_file


LINES = [f"line {i}\n" for i in range(1, 11)]  # 10 lines


# ---------------------------------------------------------------------------
# clip_lines
# ---------------------------------------------------------------------------

class TestClipLines:
    def test_full_range_returns_all(self):
        result = list(clip_lines(LINES, start=1, end=10))
        assert result == LINES

    def test_single_line(self):
        result = list(clip_lines(LINES, start=5, end=5))
        assert result == ["line 5\n"]

    def test_partial_range(self):
        result = list(clip_lines(LINES, start=3, end=6))
        assert result == ["line 3\n", "line 4\n", "line 5\n", "line 6\n"]

    def test_open_ended_reads_to_eof(self):
        result = list(clip_lines(LINES, start=8))
        assert result == ["line 8\n", "line 9\n", "line 10\n"]

    def test_start_beyond_length_returns_empty(self):
        result = list(clip_lines(LINES, start=20))
        assert result == []

    def test_end_beyond_length_returns_remaining(self):
        result = list(clip_lines(LINES, start=9, end=100))
        assert result == ["line 9\n", "line 10\n"]

    def test_start_zero_raises(self):
        with pytest.raises(ValueError, match="start must be >= 1"):
            list(clip_lines(LINES, start=0))

    def test_end_before_start_raises(self):
        with pytest.raises(ValueError, match="end"):
            list(clip_lines(LINES, start=5, end=3))

    def test_empty_input_returns_empty(self):
        assert list(clip_lines([], start=1, end=5)) == []

    def test_preserves_line_content_exactly(self):
        raw = ["2024-01-01 INFO hello\n", "2024-01-01 ERROR boom\n"]
        result = list(clip_lines(raw, start=2, end=2))
        assert result == ["2024-01-01 ERROR boom\n"]


# ---------------------------------------------------------------------------
# clip_file
# ---------------------------------------------------------------------------

def test_clip_file_writes_correct_lines(tmp_path):
    p = tmp_path / "sample.log"
    p.write_text("".join(LINES))

    import io
    buf = io.StringIO()
    count = clip_file(str(p), start=2, end=4, out=buf)
    assert count == 3
    assert buf.getvalue() == "line 2\nline 3\nline 4\n"


def test_clip_file_open_ended(tmp_path):
    p = tmp_path / "sample.log"
    p.write_text("".join(LINES))

    import io
    buf = io.StringIO()
    count = clip_file(str(p), start=9, out=buf)
    assert count == 2
    assert buf.getvalue() == "line 9\nline 10\n"
