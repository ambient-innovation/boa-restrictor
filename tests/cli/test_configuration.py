import warnings
from unittest import mock

import pytest

from boa_restrictor.cli.configuration import is_rule_excluded, is_rule_excluded_per_file, load_configuration
from boa_restrictor.exceptions.configuration import TomlParsingError
from boa_restrictor.rules import AssertRaisesProhibitedRule, AsteriskRequiredRule


@mock.patch("builtins.open", mock.mock_open(read_data=b'[tool."boa-restrictor"]\nexclude = ["PBR001"]\n'))
def test_load_configuration_exclusion_rules():
    data = load_configuration(file_path="pyproject.toml")

    assert data == {"exclude": ["PBR001"]}


@mock.patch("builtins.open", mock.mock_open(read_data=b'[tool."boa-restrictor"]\nenable_django_rules = false\n'))
def test_load_configuration_enable_django_rules_set():
    data = load_configuration(file_path="pyproject.toml")

    assert data == {"enable_django_rules": False}


@mock.patch(
    "builtins.open",
    mock.mock_open(
        read_data=b'[tool."boa-restrictor"."per-file-excludes"]\n"*/test/*" = ["PBR001"]\n',
    ),
)
def test_load_configuration_per_file_excludes():
    data = load_configuration(file_path="pyproject.toml")

    assert data == {"per-file-excludes": {"*/test/*": ["PBR001"]}}


def test_load_configuration_invalid_file():
    data = load_configuration(file_path="invalid_file.toml")

    assert data == {}


@mock.patch("builtins.open", mock.mock_open(read_data=b"invalid toml content ==="))
def test_load_configuration_invalid_toml():
    with pytest.raises(TomlParsingError, match=r"contains syntax errors\."):
        load_configuration(file_path="pyproject.toml")


@mock.patch("builtins.open", mock.mock_open(read_data=b"[tool.other_linter]\nvalue = true\n"))
def test_load_configuration_key_missing():
    data = load_configuration(file_path="pyproject.toml")

    assert data == {}


def test_is_rule_excluded_is_excluded():
    assert is_rule_excluded(rule_class=AsteriskRequiredRule, excluded_rules=["PBR001"]) is True


def test_is_django_rule_excluded_is_excluded():
    assert is_rule_excluded(rule_class=AssertRaisesProhibitedRule, excluded_rules=["DBR001"]) is True


def test_is_rule_excluded_is_not_excluded():
    assert is_rule_excluded(rule_class=AsteriskRequiredRule, excluded_rules=["PBR002"]) is False


@mock.patch.object(warnings, "warn")
def test_is_rule_excluded_invalid_rule(mocked_warn):
    assert is_rule_excluded(rule_class=AsteriskRequiredRule, excluded_rules=["PBR999"]) is False
    mocked_warn.assert_called_once()


def test_is_rule_excluded_per_file_is_excluded():
    assert (
        is_rule_excluded_per_file(
            filename="tests/test_history.py",
            rule_class=AsteriskRequiredRule,
            per_file_excluded_rules={"*.py": ["PBR001"]},
        )
        is True
    )


def test_is_rule_excluded_per_file_is_not_excluded():
    assert (
        is_rule_excluded_per_file(
            filename="tests/test_history.py",
            rule_class=AsteriskRequiredRule,
            per_file_excluded_rules={"*.py": ["PBR002"]},
        )
        is False
    )


def test_is_rule_excluded_per_file_file_not_matched():
    assert (
        is_rule_excluded_per_file(
            filename="pyproject.toml",
            rule_class=AsteriskRequiredRule,
            per_file_excluded_rules={"*.py": ["PBR002"]},
        )
        is False
    )


def test_is_rule_excluded_per_file_exclude_directory():
    assert (
        is_rule_excluded_per_file(
            filename="apps/common/file.py",
            rule_class=AsteriskRequiredRule,
            per_file_excluded_rules={"*/common/*.py": ["PBR001"]},
        )
        is True
    )


def test_is_rule_excluded_per_file_exclude_subdirectory():
    assert (
        is_rule_excluded_per_file(
            filename="apps/common/package/file.py",
            rule_class=AsteriskRequiredRule,
            per_file_excluded_rules={"*/common/**/*.py": ["PBR001"]},
        )
        is True
    )
