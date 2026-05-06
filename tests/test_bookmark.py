"""Tests for logslice.bookmark."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from logslice.bookmark import (
    delete_bookmark,
    get_bookmark,
    list_bookmarks,
    read_from_bookmark,
    set_bookmark,
)


@pytest.fixture()
def bm_file(tmp_path):
    return tmp_path / "bookmarks.json"


def test_set_and_get(bm_file):
    set_bookmark("mymark", "/var/log/app.log", 42, bm_file)
    result = get_bookmark("mymark", bm_file)
    assert result is not None
    assert result["line"] == 42
    assert result["file"].endswith("app.log")


def test_get_missing_returns_none(bm_file):
    assert get_bookmark("nonexistent", bm_file) is None


def test_overwrite_bookmark(bm_file):
    set_bookmark("x", "/tmp/a.log", 1, bm_file)
    set_bookmark("x", "/tmp/a.log", 99, bm_file)
    assert get_bookmark("x", bm_file)["line"] == 99


def test_delete_existing(bm_file):
    set_bookmark("del_me", "/tmp/f.log", 5, bm_file)
    assert delete_bookmark("del_me", bm_file) is True
    assert get_bookmark("del_me", bm_file) is None


def test_delete_nonexistent(bm_file):
    assert delete_bookmark("ghost", bm_file) is False


def test_list_empty(bm_file):
    assert list_bookmarks(bm_file) == {}


def test_list_multiple(bm_file):
    set_bookmark("a", "/tmp/a.log", 1, bm_file)
    set_bookmark("b", "/tmp/b.log", 2, bm_file)
    bms = list_bookmarks(bm_file)
    assert set(bms.keys()) == {"a", "b"}


def test_bookmark_file_is_valid_json(bm_file):
    set_bookmark("j", "/tmp/j.log", 7, bm_file)
    with bm_file.open() as fh:
        data = json.load(fh)
    assert "j" in data


def test_read_from_bookmark(tmp_path, bm_file):
    log = tmp_path / "sample.log"
    log.write_text("line0\nline1\nline2\nline3\n")
    set_bookmark("start", str(log), 2, bm_file)
    lines = read_from_bookmark("start", bm_file)
    assert lines == ["line2\n", "line3\n"]


def test_read_from_missing_bookmark_raises(bm_file):
    with pytest.raises(KeyError, match="missing"):
        read_from_bookmark("missing", bm_file)
