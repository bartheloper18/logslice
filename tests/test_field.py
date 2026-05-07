"""Tests for logslice.field."""

import pytest
from logslice.field import (
    extract_json_fields,
    extract_kv_fields,
    filter_by_field,
    get_field,
)


class TestExtractJsonFields:
    def test_valid_json_object(self):
        result = extract_json_fields('{"level": "INFO", "msg": "started"}')
        assert result == {"level": "INFO", "msg": "started"}

    def test_non_json_returns_none(self):
        assert extract_json_fields("plain text line") is None

    def test_json_array_returns_none(self):
        assert extract_json_fields('["a", "b"]') is None

    def test_invalid_json_returns_none(self):
        assert extract_json_fields('{bad json}') is None

    def test_nested_values_preserved(self):
        result = extract_json_fields('{"a": {"b": 1}}')
        assert result == {"a": {"b": 1}}


class TestExtractKvFields:
    def test_simple_kv(self):
        assert extract_kv_fields("level=INFO msg=hello") == {"level": "INFO", "msg": "hello"}

    def test_quoted_value(self):
        result = extract_kv_fields('msg="hello world" level=WARN')
        assert result["msg"] == "hello world"
        assert result["level"] == "WARN"

    def test_no_pairs_returns_empty(self):
        assert extract_kv_fields("just a plain line") == {}

    def test_dotted_key(self):
        result = extract_kv_fields("http.status=200")
        assert result["http.status"] == "200"


class TestGetField:
    def test_json_field(self):
        line = '{"level": "ERROR", "msg": "oops"}'
        assert get_field(line, "level") == "ERROR"

    def test_kv_field(self):
        assert get_field("level=DEBUG msg=ok", "level") == "DEBUG"

    def test_missing_field_returns_none(self):
        assert get_field("level=INFO", "missing") is None

    def test_json_numeric_value_as_string(self):
        assert get_field('{"code": 404}', "code") == "404"


class TestFilterByField:
    def test_basic_filter(self):
        lines = ["level=INFO msg=a", "level=ERROR msg=b", "level=INFO msg=c"]
        result = filter_by_field(lines, "level", "INFO")
        assert result == ["level=INFO msg=a", "level=INFO msg=c"]

    def test_no_matches(self):
        lines = ["level=INFO", "level=DEBUG"]
        assert filter_by_field(lines, "level", "ERROR") == []

    def test_ignore_case(self):
        lines = ["level=info", "level=ERROR"]
        result = filter_by_field(lines, "level", "INFO", ignore_case=True)
        assert result == ["level=info"]

    def test_json_lines(self):
        lines = ['{"level":"INFO"}', '{"level":"ERROR"}']
        result = filter_by_field(lines, "level", "ERROR")
        assert result == ['{"level":"ERROR"}']

    def test_line_missing_field_skipped(self):
        lines = ["no fields here", "level=INFO"]
        result = filter_by_field(lines, "level", "INFO")
        assert result == ["level=INFO"]
