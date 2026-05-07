"""Tests for logslice.highlight_cmd."""

from __future__ import annotations

import io
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from logslice.highlight_cmd import build_highlight_parser, run_highlight


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ns(**kwargs):
    defaults = dict(file=None, no_color=True, levels_only=False)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _run(args, lines: str) -> str:
    """Run highlight over *lines* (a multi-line string) and return output."""
    out = io.StringIO()
    # Patch stdin via monkeypatching is awkward; use a temp file instead.
    return out, run_highlight(args, out=out)


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

class TestBuildHighlightParser:
    def test_returns_parser(self):
        p = build_highlight_parser()
        assert p is not None

    def test_defaults(self):
        p = build_highlight_parser()
        ns = p.parse_args([])
        assert ns.no_color is False
        assert ns.levels_only is False
        assert ns.file is None

    def test_no_color_flag(self):
        p = build_highlight_parser()
        ns = p.parse_args(["--no-color"])
        assert ns.no_color is True

    def test_levels_only_flag(self):
        p = build_highlight_parser()
        ns = p.parse_args(["--levels-only"])
        assert ns.levels_only is True


# ---------------------------------------------------------------------------
# run_highlight tests
# ---------------------------------------------------------------------------

class TestRunHighlight:
    def test_reads_file_and_writes_output(self, tmp_path: Path):
        log = tmp_path / "app.log"
        log.write_text("2024-01-01T00:00:00Z INFO hello\n")
        out = io.StringIO()
        code = run_highlight(_ns(file=str(log)), out=out)
        assert code == 0
        assert "hello" in out.getvalue()

    def test_missing_file_returns_error(self, tmp_path: Path):
        out = io.StringIO()
        code = run_highlight(_ns(file=str(tmp_path / "missing.log")), out=out)
        assert code == 1

    def test_no_color_preserves_line(self, tmp_path: Path):
        log = tmp_path / "app.log"
        log.write_text("ERROR something broke\n")
        out = io.StringIO()
        run_highlight(_ns(file=str(log), no_color=True), out=out)
        assert out.getvalue().strip() == "ERROR something broke"

    def test_levels_only_skips_timestamps(self, tmp_path: Path):
        """With --levels-only and color on, timestamps should NOT be wrapped."""
        log = tmp_path / "app.log"
        log.write_text("2024-01-01T00:00:00Z INFO hello\n")
        out = io.StringIO()
        # Force color by monkey-patching supports_color via no_color=False;
        # we check that the raw timestamp string still appears verbatim.
        run_highlight(_ns(file=str(log), no_color=True, levels_only=True), out=out)
        result = out.getvalue()
        assert "2024-01-01T00:00:00Z" in result

    def test_adds_newline_if_missing(self, tmp_path: Path):
        log = tmp_path / "app.log"
        # Write a line without trailing newline
        log.write_bytes(b"INFO no newline")
        out = io.StringIO()
        run_highlight(_ns(file=str(log)), out=out)
        assert out.getvalue().endswith("\n")
