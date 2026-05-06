"""Tests for logslice.redact_cmd."""

import io
import pytest
from argparse import Namespace
from logslice.redact_cmd import run_redact, build_redact_parser


def _ns(**kwargs):
    defaults = dict(files=[], patterns=[], builtins=[], mask="[REDACTED]", ignore_case=False)
    defaults.update(kwargs)
    return Namespace(**defaults)


# ---------------------------------------------------------------------------
# build_redact_parser
# ---------------------------------------------------------------------------

def test_parser_defaults():
    parser = build_redact_parser()
    args = parser.parse_args(["-b", "ipv4"])
    assert args.builtins == ["ipv4"]
    assert args.mask == "[REDACTED]"
    assert args.ignore_case is False


def test_parser_custom_mask():
    parser = build_redact_parser()
    args = parser.parse_args(["-p", r"\d+", "-m", "***"])
    assert args.mask == "***"


# ---------------------------------------------------------------------------
# run_redact — no files (stdin-like)
# ---------------------------------------------------------------------------

def test_no_pattern_returns_error():
    out = io.StringIO()
    rc = run_redact(_ns(), out=out)
    assert rc == 1


def test_unknown_builtin_returns_error():
    out = io.StringIO()
    rc = run_redact(_ns(builtins=["badname"]), out=out)
    assert rc == 1


# ---------------------------------------------------------------------------
# run_redact — with file
# ---------------------------------------------------------------------------

def test_redacts_file_content(tmp_path):
    f = tmp_path / "app.log"
    f.write_text("ip 10.0.0.1 connected\nclean\n")
    out = io.StringIO()
    rc = run_redact(_ns(files=[str(f)], builtins=["ipv4"]), out=out)
    assert rc == 0
    output = out.getvalue()
    assert "10.0.0.1" not in output
    assert "[REDACTED]" in output
    assert "clean" in output


def test_missing_file_returns_error(tmp_path):
    out = io.StringIO()
    rc = run_redact(_ns(files=["/nonexistent/path.log"], patterns=[r"x"]), out=out)
    assert rc == 1


def test_multiple_files(tmp_path):
    f1 = tmp_path / "a.log"
    f2 = tmp_path / "b.log"
    f1.write_text("hello secret\n")
    f2.write_text("world secret\n")
    out = io.StringIO()
    rc = run_redact(_ns(files=[str(f1), str(f2)], patterns=["secret"]), out=out)
    assert rc == 0
    lines = out.getvalue().splitlines()
    assert len(lines) == 2
    assert all("[REDACTED]" in l for l in lines)
