"""Tests for logslice.context module."""

import re
import pytest
from logslice.context import (
    ContextLine,
    context_grep,
    format_context_output,
    SEPARATOR,
)


LINES = [
    "line1: INFO  boot",
    "line2: DEBUG init",
    "line3: ERROR crash",
    "line4: INFO  recover",
    "line5: DEBUG cleanup",
    "line6: ERROR timeout",
    "line7: INFO  done",
]


def pat(s):
    return re.compile(s)


class TestContextGrep:
    def test_match_only_no_context(self):
        results = list(context_grep(LINES, pat("ERROR")))
        assert len(results) == 2
        assert all(r.is_match for r in results)
        assert results[0].lineno == 3
        assert results[1].lineno == 6

    def test_before_context(self):
        results = list(context_grep(LINES, pat("ERROR"), before=1))
        linenos = [r.lineno for r in results]
        assert 2 in linenos  # before line3
        assert 3 in linenos  # match
        assert 5 in linenos  # before line6
        assert 6 in linenos  # match

    def test_after_context(self):
        results = list(context_grep(LINES, pat("ERROR"), after=1))
        linenos = [r.lineno for r in results]
        assert 3 in linenos  # match
        assert 4 in linenos  # after line3
        assert 6 in linenos  # match
        assert 7 in linenos  # after line6

    def test_before_and_after(self):
        results = list(context_grep(LINES, pat("ERROR"), before=1, after=1))
        linenos = [r.lineno for r in results]
        assert 2 in linenos
        assert 3 in linenos
        assert 4 in linenos
        assert 5 in linenos
        assert 6 in linenos
        assert 7 in linenos

    def test_no_duplicate_lines(self):
        results = list(context_grep(LINES, pat("ERROR"), before=2, after=2))
        linenos = [r.lineno for r in results]
        assert len(linenos) == len(set(linenos))

    def test_invert_match(self):
        results = list(context_grep(LINES, pat("ERROR"), invert=True))
        assert all(r.is_match for r in results)
        assert all("ERROR" not in r.text for r in results)
        assert len(results) == 5

    def test_no_matches(self):
        results = list(context_grep(LINES, pat("CRITICAL")))
        assert results == []

    def test_match_is_match_flag(self):
        results = list(context_grep(LINES, pat("ERROR"), before=1))
        match_lines = [r for r in results if r.is_match]
        context_lines = [r for r in results if not r.is_match]
        assert len(match_lines) == 2
        assert len(context_lines) == 2


class TestFormatContextOutput:
    def test_plain_output(self):
        results = list(context_grep(LINES, pat("ERROR")))
        output = list(format_context_output(results))
        assert len(output) == 3  # 2 matches + 1 separator
        assert output[1] == SEPARATOR

    def test_no_separator_when_adjacent(self):
        results = list(context_grep(LINES, pat("ERROR"), before=1, after=1))
        output = list(format_context_output(results))
        # lines 2-4 and 5-7 are adjacent, no separator expected
        assert SEPARATOR not in output

    def test_show_lineno(self):
        results = list(context_grep(LINES, pat("ERROR")))
        output = list(format_context_output(results, show_lineno=True))
        assert output[0].startswith("3:")

    def test_no_lineno_by_default(self):
        results = list(context_grep(LINES, pat("ERROR")))
        output = list(format_context_output(results))
        assert not output[0][0].isdigit()

    def test_strips_trailing_newline(self):
        lines_with_newlines = [l + "\n" for l in LINES]
        results = list(context_grep(lines_with_newlines, pat("ERROR")))
        output = list(format_context_output(results))
        assert not any(o.endswith("\n") for o in output if o != SEPARATOR)
