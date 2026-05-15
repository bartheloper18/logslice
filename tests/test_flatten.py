"""Tests for logslice.flatten."""

from __future__ import annotations

import json

import pytest

from logslice.flatten import _flatten_dict, flatten_line, flatten_lines


# ---------------------------------------------------------------------------
# _flatten_dict
# ---------------------------------------------------------------------------

class TestFlattenDict:
    def test_already_flat(self):
        assert _flatten_dict({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    def test_one_level_nested(self):
        result = _flatten_dict({"a": {"b": 1}})
        assert result == {"a.b": 1}

    def test_two_levels_nested(self):
        result = _flatten_dict({"a": {"b": {"c": 42}}})
        assert result == {"a.b.c": 42}

    def test_list_of_scalars(self):
        result = _flatten_dict({"tags": ["x", "y"]})
        assert result == {"tags.0": "x", "tags.1": "y"}

    def test_list_of_dicts(self):
        result = _flatten_dict({"items": [{"id": 1}, {"id": 2}]})
        assert result == {"items.0.id": 1, "items.1.id": 2}

    def test_custom_separator(self):
        result = _flatten_dict({"a": {"b": 3}}, sep="_")
        assert result == {"a_b": 3}

    def test_empty_dict(self):
        assert _flatten_dict({}) == {}


# ---------------------------------------------------------------------------
# flatten_line
# ---------------------------------------------------------------------------

class TestFlattenLine:
    def test_flat_json_unchanged_structure(self):
        line = '{"level": "info", "msg": "ok"}\n'
        result = flatten_line(line)
        parsed = json.loads(result)
        assert parsed == {"level": "info", "msg": "ok"}

    def test_nested_json_flattened(self):
        line = '{"a": {"b": 1}}\n'
        result = flatten_line(line)
        assert json.loads(result) == {"a.b": 1}

    def test_trailing_newline_preserved(self):
        line = '{"x": {"y": 2}}\n'
        assert flatten_line(line).endswith("\n")

    def test_no_trailing_newline_preserved(self):
        line = '{"x": {"y": 2}}'
        assert not flatten_line(line).endswith("\n")

    def test_non_json_returned_unchanged(self):
        line = "2024-01-01 INFO hello world\n"
        assert flatten_line(line) == line

    def test_json_array_returned_unchanged(self):
        line = '[1, 2, 3]\n'
        assert flatten_line(line) == line

    def test_invalid_json_returned_unchanged(self):
        line = '{not valid json}\n'
        assert flatten_line(line) == line

    def test_custom_sep(self):
        line = '{"a": {"b": 5}}'
        result = flatten_line(line, sep="/")
        assert json.loads(result) == {"a/b": 5}


# ---------------------------------------------------------------------------
# flatten_lines
# ---------------------------------------------------------------------------

def test_flatten_lines_mixed_input():
    lines = [
        '{"a": {"b": 1}}\n',
        'plain text line\n',
        '{"x": 2}\n',
    ]
    results = list(flatten_lines(iter(lines)))
    assert json.loads(results[0]) == {"a.b": 1}
    assert results[1] == 'plain text line\n'
    assert json.loads(results[2]) == {"x": 2}


def test_flatten_lines_empty():
    assert list(flatten_lines(iter([]))) == []
