"""Tests for logslice.redact."""

import pytest
from logslice.redact import (
    BUILTIN_PATTERNS,
    compile_redact_patterns,
    redact_line,
    redact_lines,
    redact_file,
    DEFAULT_MASK,
)


# ---------------------------------------------------------------------------
# compile_redact_patterns
# ---------------------------------------------------------------------------

def test_custom_pattern_compiles():
    pats = compile_redact_patterns([r"\d+"])
    assert len(pats) == 1


def test_builtin_ipv4_compiles():
    pats = compile_redact_patterns([], builtins=["ipv4"])
    assert len(pats) == 1


def test_unknown_builtin_raises():
    with pytest.raises(ValueError, match="Unknown built-in"):
        compile_redact_patterns([], builtins=["nonexistent"])


def test_combined_patterns():
    pats = compile_redact_patterns([r"foo"], builtins=["email"])
    assert len(pats) == 2


# ---------------------------------------------------------------------------
# redact_line
# ---------------------------------------------------------------------------

def test_redact_ip_address():
    pats = compile_redact_patterns([], builtins=["ipv4"])
    result, count = redact_line("Connected from 192.168.1.1 ok", pats)
    assert "192.168.1.1" not in result
    assert DEFAULT_MASK in result
    assert count == 1


def test_redact_email():
    pats = compile_redact_patterns([], builtins=["email"])
    result, count = redact_line("user: alice@example.com logged in", pats)
    assert "alice@example.com" not in result
    assert count == 1


def test_no_match_returns_original():
    pats = compile_redact_patterns([r"NOMATCH"])
    result, count = redact_line("nothing here", pats)
    assert result == "nothing here"
    assert count == 0


def test_custom_mask():
    pats = compile_redact_patterns([r"secret"])
    result, _ = redact_line("my secret value", pats, mask="***")
    assert result == "my *** value"


def test_multiple_patterns_applied():
    pats = compile_redact_patterns([r"foo", r"bar"])
    result, count = redact_line("foo and bar", pats)
    assert "foo" not in result
    assert "bar" not in result
    assert count == 2


# ---------------------------------------------------------------------------
# redact_lines
# ---------------------------------------------------------------------------

def test_redact_lines_iterator():
    pats = compile_redact_patterns([r"\d+"])
    lines = ["line 123\n", "no digits\n", "456 end\n"]
    result = list(redact_lines(lines, pats))
    assert DEFAULT_MASK in result[0]
    assert result[1] == "no digits\n"
    assert DEFAULT_MASK in result[2]


def test_redact_lines_empty():
    pats = compile_redact_patterns([r"x"])
    assert list(redact_lines([], pats)) == []


# ---------------------------------------------------------------------------
# redact_file
# ---------------------------------------------------------------------------

def test_redact_file(tmp_path):
    f = tmp_path / "log.txt"
    f.write_text("token abc123xyz987qwerty\nclean line\n")
    pats = compile_redact_patterns([], builtins=["token"])
    lines = list(redact_file(str(f), pats))
    assert len(lines) == 2
    assert "clean line" in lines[1]
