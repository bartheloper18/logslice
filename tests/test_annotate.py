"""Tests for logslice.annotate and logslice.annotate_cmd."""

from __future__ import annotations

import argparse
import io

import pytest

from logslice.annotate import AnnotatedLine, annotate_lines, format_annotated
from logslice.annotate_cmd import build_annotate_parser, run_annotate


ISO_LINES = [
    "2024-01-01T00:00:00 INFO  boot\n",
    "2024-01-01T00:00:01 INFO  ready\n",
    "2024-01-01T00:00:03 ERROR crash\n",
]

PLAIN_LINES = ["hello\n", "world\n"]


# ---------------------------------------------------------------------------
# annotate_lines
# ---------------------------------------------------------------------------

class TestAnnotateLines:
    def test_lineno_starts_at_one(self):
        results = list(annotate_lines(PLAIN_LINES))
        assert results[0].lineno == 1
        assert results[1].lineno == 2

    def test_text_preserved(self):
        results = list(annotate_lines(PLAIN_LINES))
        assert results[0].text == "hello\n"

    def test_elapsed_none_for_plain_lines(self):
        results = list(annotate_lines(PLAIN_LINES, show_elapsed=True))
        assert all(r.elapsed_ms is None for r in results)

    def test_elapsed_zero_for_first_ts_line(self):
        results = list(annotate_lines(ISO_LINES, show_elapsed=True))
        assert results[0].elapsed_ms == pytest.approx(0.0)

    def test_elapsed_increases(self):
        results = list(annotate_lines(ISO_LINES, show_elapsed=True))
        assert results[1].elapsed_ms == pytest.approx(1000.0)
        assert results[2].elapsed_ms == pytest.approx(3000.0)

    def test_delta_none_for_first_ts_line(self):
        results = list(annotate_lines(ISO_LINES, show_delta=True))
        assert results[0].delta_ms is None

    def test_delta_between_lines(self):
        results = list(annotate_lines(ISO_LINES, show_delta=True))
        assert results[1].delta_ms == pytest.approx(1000.0)
        assert results[2].delta_ms == pytest.approx(2000.0)

    def test_elapsed_and_delta_together(self):
        results = list(annotate_lines(ISO_LINES, show_elapsed=True, show_delta=True))
        assert results[2].elapsed_ms == pytest.approx(3000.0)
        assert results[2].delta_ms == pytest.approx(2000.0)


# ---------------------------------------------------------------------------
# format_annotated
# ---------------------------------------------------------------------------

class TestFormatAnnotated:
    def _ann(self, lineno=1, text="hello\n", elapsed_ms=None, delta_ms=None):
        return AnnotatedLine(lineno=lineno, text=text, elapsed_ms=elapsed_ms, delta_ms=delta_ms)

    def test_no_flags_returns_text_with_newline(self):
        ann = self._ann()
        result = format_annotated(ann, show_lineno=False, show_elapsed=False, show_delta=False)
        assert result == "hello\n"

    def test_lineno_prefix_present(self):
        ann = self._ann(lineno=42)
        result = format_annotated(ann, show_lineno=True, show_elapsed=False, show_delta=False)
        assert "[    42]" in result

    def test_elapsed_shown_as_ms(self):
        ann = self._ann(elapsed_ms=1500.0)
        result = format_annotated(ann, show_lineno=False, show_elapsed=True, show_delta=False)
        assert "1500.0" in result
        assert "ms" in result

    def test_elapsed_dash_when_none(self):
        ann = self._ann(elapsed_ms=None)
        result = format_annotated(ann, show_lineno=False, show_elapsed=True, show_delta=False)
        assert "-" in result

    def test_delta_shown(self):
        ann = self._ann(delta_ms=250.5)
        result = format_annotated(ann, show_lineno=False, show_elapsed=False, show_delta=True)
        assert "250.5" in result

    def test_trailing_newline_always_present(self):
        ann = self._ann(text="no newline")
        result = format_annotated(ann, show_lineno=True, show_elapsed=False, show_delta=False)
        assert result.endswith("\n")


# ---------------------------------------------------------------------------
# annotate_cmd
# ---------------------------------------------------------------------------

def _ns(**kwargs) -> argparse.Namespace:
    defaults = dict(file="-", lineno=True, elapsed=False, delta=False, output="-")
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestRunAnnotate:
    def _run(self, lines, **kwargs):
        out = io.StringIO()
        ns = _ns(**kwargs)
        ns.file = "-"
        import unittest.mock as mock
        with mock.patch("sys.stdin", io.StringIO("".join(lines))):
            run_annotate(ns, out=out)
        return out.getvalue()

    def test_lineno_in_output(self):
        result = self._run(PLAIN_LINES, lineno=True)
        assert "[     1]" in result
        assert "[     2]" in result

    def test_no_lineno_omitted(self):
        result = self._run(PLAIN_LINES, lineno=False)
        assert "[" not in result

    def test_elapsed_in_output(self):
        result = self._run(ISO_LINES, lineno=False, elapsed=True)
        assert "ms" in result

    def test_missing_file_returns_1(self, tmp_path):
        out = io.StringIO()
        ns = _ns(file=str(tmp_path / "no_such.log"))
        rc = run_annotate(ns, out=out)
        assert rc == 1

    def test_real_file(self, tmp_path):
        f = tmp_path / "sample.log"
        f.write_text("".join(ISO_LINES))
        out = io.StringIO()
        ns = _ns(file=str(f), lineno=True, elapsed=True, delta=True)
        rc = run_annotate(ns, out=out)
        assert rc == 0
        assert "[     1]" in out.getvalue()


class TestBuildAnnotateParser:
    def test_returns_parser(self):
        p = build_annotate_parser()
        assert isinstance(p, argparse.ArgumentParser)

    def test_defaults(self):
        p = build_annotate_parser()
        args = p.parse_args([])
        assert args.lineno is True
        assert args.elapsed is False
        assert args.delta is False

    def test_no_lineno_flag(self):
        p = build_annotate_parser()
        args = p.parse_args(["--no-lineno"])
        assert args.lineno is False

    def test_elapsed_flag(self):
        p = build_annotate_parser()
        args = p.parse_args(["-e"])
        assert args.elapsed is True

    def test_delta_flag(self):
        p = build_annotate_parser()
        args = p.parse_args(["-d"])
        assert args.delta is True
