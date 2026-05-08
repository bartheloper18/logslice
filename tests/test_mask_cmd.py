"""Tests for logslice.mask_cmd."""

from __future__ import annotations

import io
import types

import pytest

from logslice.mask_cmd import build_mask_parser, run_mask


def _ns(**kwargs):
    defaults = dict(file=None, pattern=None, field=None,
                    placeholder="***", output=None)
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _run(args, lines: list[str]) -> tuple[int, str]:
    """Run run_mask with *args*, feeding *lines* via a StringIO, return (rc, output)."""
    import unittest.mock as mock

    out = io.StringIO()
    stdin_data = io.StringIO("".join(lines))
    with mock.patch("sys.stdin", stdin_data):
        rc = run_mask(args, out=out)
    return rc, out.getvalue()


class TestBuildMaskParser:
    def test_returns_parser(self):
        p = build_mask_parser()
        assert p is not None

    def test_defaults(self):
        p = build_mask_parser()
        args = p.parse_args([])
        assert args.placeholder == "***"
        assert args.pattern is None
        assert args.field is None

    def test_pattern_flag(self):
        p = build_mask_parser()
        args = p.parse_args(["-p", r"\d+"])
        assert args.pattern == r"\d+"

    def test_field_flag(self):
        p = build_mask_parser()
        args = p.parse_args(["-f", "token"])
        assert args.field == "token"

    def test_custom_placeholder(self):
        p = build_mask_parser()
        args = p.parse_args(["--placeholder", "XXXX", "-f", "pw"])
        assert args.placeholder == "XXXX"


class TestRunMask:
    def test_no_pattern_or_field_returns_error(self):
        rc, _ = _run(_ns(), ["line\n"])
        assert rc == 1

    def test_invalid_regex_returns_error(self):
        rc, _ = _run(_ns(pattern="[unclosed"), ["line\n"])
        assert rc == 1

    def test_masks_pattern_from_stdin(self):
        rc, out = _run(_ns(pattern=r"\d+"), ["count=42\n", "total=7\n"])
        assert rc == 0
        assert "count=***" in out
        assert "total=***" in out

    def test_masks_field_from_stdin(self):
        rc, out = _run(_ns(field="user"), ["user=alice level=INFO\n"])
        assert rc == 0
        assert "user=***" in out
        assert "level=INFO" in out

    def test_custom_placeholder(self):
        rc, out = _run(_ns(pattern=r"\d+", placeholder="[N]"), ["x=99\n"])
        assert rc == 0
        assert "[N]" in out
        assert "99" not in out
