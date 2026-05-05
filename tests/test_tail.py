"""Tests for logslice.tail."""

import os
import tempfile
import threading
import time

import pytest

from logslice.tail import read_last_lines, follow_file


# ---------------------------------------------------------------------------
# read_last_lines
# ---------------------------------------------------------------------------

class TestReadLastLines:
    def _write(self, path, lines):
        with open(path, "w") as fh:
            fh.writelines(lines)

    def test_returns_last_n(self, tmp_path):
        p = tmp_path / "log.txt"
        all_lines = [f"line {i}\n" for i in range(20)]
        self._write(str(p), all_lines)
        result = read_last_lines(str(p), 5)
        assert result == all_lines[-5:]

    def test_n_larger_than_file(self, tmp_path):
        p = tmp_path / "log.txt"
        all_lines = [f"line {i}\n" for i in range(3)]
        self._write(str(p), all_lines)
        result = read_last_lines(str(p), 10)
        assert len(result) == 3

    def test_n_zero_returns_empty(self, tmp_path):
        p = tmp_path / "log.txt"
        p.write_text("hello\n")
        assert read_last_lines(str(p), 0) == []

    def test_single_line_file(self, tmp_path):
        p = tmp_path / "log.txt"
        p.write_text("only line\n")
        result = read_last_lines(str(p), 1)
        assert result == ["only line\n"]

    def test_exact_n_lines(self, tmp_path):
        p = tmp_path / "log.txt"
        lines = [f"{i}\n" for i in range(5)]
        self._write(str(p), lines)
        result = read_last_lines(str(p), 5)
        assert result == lines


# ---------------------------------------------------------------------------
# follow_file
# ---------------------------------------------------------------------------

class TestFollowFile:
    def test_picks_up_appended_lines(self, tmp_path):
        p = tmp_path / "live.log"
        p.write_text("")  # create empty file

        collected: list[str] = []

        def _write_later():
            time.sleep(0.05)
            with open(str(p), "a") as fh:
                fh.write("new line 1\n")
                fh.write("new line 2\n")

        t = threading.Thread(target=_write_later, daemon=True)
        t.start()

        follow_file(str(p), collected.append, poll_interval=0.02, stop_after=2)
        t.join(timeout=2)

        assert len(collected) == 2
        assert collected[0] == "new line 1\n"
        assert collected[1] == "new line 2\n"

    def test_stop_after_limits_lines(self, tmp_path):
        p = tmp_path / "live.log"
        p.write_text("")  # empty

        collected: list[str] = []

        def _write_many():
            time.sleep(0.05)
            with open(str(p), "a") as fh:
                for i in range(10):
                    fh.write(f"line {i}\n")

        t = threading.Thread(target=_write_many, daemon=True)
        t.start()

        follow_file(str(p), collected.append, poll_interval=0.02, stop_after=3)
        t.join(timeout=2)

        assert len(collected) == 3
