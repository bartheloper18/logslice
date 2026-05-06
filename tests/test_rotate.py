"""Tests for logslice.rotate."""

from __future__ import annotations

import gzip
import textwrap
from pathlib import Path

import pytest

from logslice.rotate import find_rotated_files, iter_rotated_lines, open_rotated


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content), encoding='utf-8')
    return path


def _write_gz(path: Path, content: str) -> Path:
    with gzip.open(path, 'wt', encoding='utf-8') as fh:
        fh.write(textwrap.dedent(content))
    return path


# ---------------------------------------------------------------------------
# find_rotated_files
# ---------------------------------------------------------------------------

class TestFindRotatedFiles:
    def test_only_base_when_no_siblings(self, tmp_path):
        base = _write(tmp_path / 'app.log', 'line\n')
        result = find_rotated_files(base)
        assert result == [base]

    def test_includes_numbered_siblings(self, tmp_path):
        base = _write(tmp_path / 'app.log', 'cur\n')
        r1 = _write(tmp_path / 'app.log.1', 'prev\n')
        r2 = _write(tmp_path / 'app.log.2', 'older\n')
        result = find_rotated_files(base)
        assert result == [base, r1, r2]

    def test_includes_gz_by_default(self, tmp_path):
        base = _write(tmp_path / 'app.log', 'cur\n')
        r1 = _write(tmp_path / 'app.log.1', 'prev\n')
        r2 = _write_gz(tmp_path / 'app.log.2.gz', 'older\n')
        result = find_rotated_files(base)
        assert r2 in result

    def test_excludes_gz_when_flag_false(self, tmp_path):
        base = _write(tmp_path / 'app.log', 'cur\n')
        _write_gz(tmp_path / 'app.log.1.gz', 'prev\n')
        result = find_rotated_files(base, include_gz=False)
        assert all(p.suffix != '.gz' for p in result)

    def test_ignores_unrelated_files(self, tmp_path):
        base = _write(tmp_path / 'app.log', 'cur\n')
        _write(tmp_path / 'other.log.1', 'nope\n')
        result = find_rotated_files(base)
        assert result == [base]


# ---------------------------------------------------------------------------
# open_rotated
# ---------------------------------------------------------------------------

def test_open_rotated_plain(tmp_path):
    p = _write(tmp_path / 'app.log', 'hello\n')
    with open_rotated(p) as fh:
        assert fh.read() == 'hello\n'


def test_open_rotated_gz(tmp_path):
    p = _write_gz(tmp_path / 'app.log.1.gz', 'compressed\n')
    with open_rotated(p) as fh:
        assert fh.read() == 'compressed\n'


# ---------------------------------------------------------------------------
# iter_rotated_lines
# ---------------------------------------------------------------------------

def test_iter_rotated_lines_order(tmp_path):
    """Lines from oldest rotated file appear before newer ones."""
    _write(tmp_path / 'app.log', 'current\n')
    _write(tmp_path / 'app.log.1', 'previous\n')
    _write(tmp_path / 'app.log.2', 'oldest\n')

    lines = list(iter_rotated_lines(tmp_path / 'app.log'))
    assert lines.index('oldest\n') < lines.index('previous\n')
    assert lines.index('previous\n') < lines.index('current\n')


def test_iter_rotated_lines_single_file(tmp_path):
    _write(tmp_path / 'app.log', 'only\n')
    assert list(iter_rotated_lines(tmp_path / 'app.log')) == ['only\n']
