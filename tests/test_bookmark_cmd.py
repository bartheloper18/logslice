"""Tests for logslice.bookmark_cmd."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pytest

from logslice.bookmark_cmd import run_bookmark


@pytest.fixture()
def bm_file(tmp_path):
    return tmp_path / "bm.json"


def _out():
    return io.StringIO()


def test_set_action(bm_file, tmp_path):
    out = _out()
    code = run_bookmark("set", name="mk", filepath=str(tmp_path / "f.log"), line=10, bookmark_file=bm_file, out=out)
    assert code == 0
    assert "mk" in out.getvalue()


def test_get_action(bm_file, tmp_path):
    logfile = str(tmp_path / "f.log")
    run_bookmark("set", name="mk", filepath=logfile, line=5, bookmark_file=bm_file, out=_out())
    out = _out()
    code = run_bookmark("get", name="mk", bookmark_file=bm_file, out=out)
    assert code == 0
    assert ":5" in out.getvalue()


def test_get_missing(bm_file):
    out = _out()
    code = run_bookmark("get", name="nope", bookmark_file=bm_file, out=out)
    assert code == 2


def test_delete_action(bm_file, tmp_path):
    run_bookmark("set", name="d", filepath=str(tmp_path / "f.log"), line=1, bookmark_file=bm_file, out=_out())
    out = _out()
    code = run_bookmark("delete", name="d", bookmark_file=bm_file, out=out)
    assert code == 0
    assert "deleted" in out.getvalue()


def test_delete_missing(bm_file):
    code = run_bookmark("delete", name="ghost", bookmark_file=bm_file, out=_out())
    assert code == 2


def test_list_empty(bm_file):
    out = _out()
    code = run_bookmark("list", bookmark_file=bm_file, out=out)
    assert code == 0
    assert "No bookmarks" in out.getvalue()


def test_list_shows_entries(bm_file, tmp_path):
    run_bookmark("set", name="alpha", filepath=str(tmp_path / "a.log"), line=3, bookmark_file=bm_file, out=_out())
    out = _out()
    run_bookmark("list", bookmark_file=bm_file, out=out)
    assert "alpha" in out.getvalue()


def test_unknown_action(bm_file):
    code = run_bookmark("fly", bookmark_file=bm_file, out=_out())
    assert code == 1


def test_set_missing_name(bm_file):
    code = run_bookmark("set", filepath="/tmp/f.log", bookmark_file=bm_file, out=_out())
    assert code == 1
