"""Tests for logslice.mask."""

from __future__ import annotations

import re
import pytest

from logslice.mask import mask_positions, mask_pattern, mask_field, mask_lines


# ---------------------------------------------------------------------------
# mask_positions
# ---------------------------------------------------------------------------

class TestMaskPositions:
    def test_middle_of_line(self):
        assert mask_positions("hello world", 6, 11) == "hello ***"

    def test_start_of_line(self):
        assert mask_positions("secretdata", 0, 6) == "***data"

    def test_invalid_range_returns_unchanged(self):
        assert mask_positions("hello", 4, 2) == "hello"

    def test_out_of_bounds_returns_unchanged(self):
        assert mask_positions("hi", 0, 10) == "hi"

    def test_custom_placeholder(self):
        assert mask_positions("abcdef", 2, 4, placeholder="[HIDDEN]") == "ab[HIDDEN]ef"


# ---------------------------------------------------------------------------
# mask_pattern
# ---------------------------------------------------------------------------

class TestMaskPattern:
    def test_simple_word(self):
        pat = re.compile(r"\d+")
        assert mask_pattern("user=42 count=7", pat) == "user=*** count=***"

    def test_no_match_unchanged(self):
        pat = re.compile(r"\d+")
        assert mask_pattern("no digits here", pat) == "no digits here"

    def test_custom_placeholder(self):
        pat = re.compile(r"password=\S+")
        result = mask_pattern("password=secret next", pat, placeholder="<REDACTED>")
        assert result == "<REDACTED> next"

    def test_capture_group(self):
        pat = re.compile(r"token=(\S+)")
        result = mask_pattern("token=abc123 end", pat, group=1)
        assert result == "token=*** end"


# ---------------------------------------------------------------------------
# mask_field
# ---------------------------------------------------------------------------

class TestMaskField:
    def test_masks_value(self):
        assert mask_field("user=alice level=INFO", "user") == "user=*** level=INFO"

    def test_field_not_present_unchanged(self):
        assert mask_field("level=INFO msg=hello", "user") == "level=INFO msg=hello"

    def test_custom_placeholder(self):
        result = mask_field("ip=192.168.1.1 port=80", "ip", placeholder="[IP]")
        assert result == "ip=[IP] port=80"


# ---------------------------------------------------------------------------
# mask_lines
# ---------------------------------------------------------------------------

class TestMaskLines:
    def test_applies_pattern_to_all_lines(self):
        lines = ["user=alice\n", "user=bob\n"]
        pat = re.compile(r"(?<=user=)\S+")
        result = list(mask_lines(lines, pattern=pat))
        assert result == ["user=***\n", "user=***\n"]

    def test_applies_field_mask(self):
        lines = ["token=xyz123 ok\n"]
        result = list(mask_lines(lines, field="token"))
        assert result == ["token=*** ok\n"]

    def test_preserves_trailing_newline(self):
        lines = ["a=1\n", "b=2"]
        result = list(mask_lines(lines, field="a"))
        assert result[0].endswith("\n")
        assert not result[1].endswith("\n")

    def test_both_pattern_and_field(self):
        lines = ["ip=1.2.3.4 secret=abc\n"]
        pat = re.compile(r"(?<=ip=)[\d.]+")
        result = list(mask_lines(lines, pattern=pat, field="secret"))
        assert "ip=***" in result[0]
        assert "secret=***" in result[0]
