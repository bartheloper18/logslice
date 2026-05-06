"""Tests for logslice.merge — multi-file chronological merge."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from logslice.merge import merge_files, merge_to_file


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, name: str, lines: list[str]) -> str:
    p = tmp_path / name
    p.write_text("\n".join(lines) + "\n")
    return str(p)


# ---------------------------------------------------------------------------
# merge_files
# ---------------------------------------------------------------------------

class TestMergeFiles:
    def test_single_file_order_preserved(self, tmp_path):
        f = _write(tmp_path, "a.log", [
            "2024-01-01T10:00:00 alpha",
            "2024-01-01T10:01:00 beta",
        ])
        result = list(merge_files([f]))
        assert result == ["2024-01-01T10:00:00 alpha", "2024-01-01T10:01:00 beta"]

    def test_two_files_interleaved(self, tmp_path):
        f1 = _write(tmp_path, "a.log", [
            "2024-01-01T10:00:00 a-first",
            "2024-01-01T10:02:00 a-second",
        ])
        f2 = _write(tmp_path, "b.log", [
            "2024-01-01T10:01:00 b-first",
            "2024-01-01T10:03:00 b-second",
        ])
        result = list(merge_files([f1, f2]))
        assert result == [
            "2024-01-01T10:00:00 a-first",
            "2024-01-01T10:01:00 b-first",
            "2024-01-01T10:02:00 a-second",
            "2024-01-01T10:03:00 b-second",
        ]

    def test_tag_prefixes_source_filename(self, tmp_path):
        f = _write(tmp_path, "app.log", ["2024-01-01T09:00:00 hello"])
        result = list(merge_files([f], tag=True))
        assert result[0].startswith("app.log: ")

    def test_lines_without_timestamp_follow_previous(self, tmp_path):
        f = _write(tmp_path, "a.log", [
            "2024-01-01T10:00:00 start",
            "  continuation line",
        ])
        result = list(merge_files([f]))
        # Both lines should be present
        assert len(result) == 2
        assert result[1] == "  continuation line"

    def test_skip_unparsed_drops_headerless_lines(self, tmp_path):
        f = _write(tmp_path, "a.log", [
            "no timestamp here",
            "2024-01-01T10:00:00 valid",
        ])
        result = list(merge_files([f], skip_unparsed=True))
        assert all("valid" in l or l.startswith("2024") for l in result)
        assert not any("no timestamp" in l for l in result)

    def test_missing_file_raises_os_error(self, tmp_path):
        with pytest.raises(OSError, match="Cannot open"):
            list(merge_files([str(tmp_path / "nonexistent.log")]))


# ---------------------------------------------------------------------------
# merge_to_file
# ---------------------------------------------------------------------------

class TestMergeToFile:
    def test_writes_correct_line_count(self, tmp_path):
        f1 = _write(tmp_path, "x.log", ["2024-01-01T08:00:00 x"])
        f2 = _write(tmp_path, "y.log", ["2024-01-01T08:01:00 y"])
        out = str(tmp_path / "merged.log")
        count = merge_to_file([f1, f2], out)
        assert count == 2

    def test_output_file_content_is_sorted(self, tmp_path):
        f1 = _write(tmp_path, "p.log", ["2024-01-01T12:00:00 p"])
        f2 = _write(tmp_path, "q.log", ["2024-01-01T11:00:00 q"])
        out = str(tmp_path / "out.log")
        merge_to_file([f1, f2], out)
        lines = Path(out).read_text().splitlines()
        assert lines[0].endswith(" q")
        assert lines[1].endswith(" p")
