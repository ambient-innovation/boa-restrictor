import os
import re
import sys
import warnings

import pytest

from boa_restrictor.exceptions.configuration import TomlParsingError
from boa_restrictor.rules import AssertRaisesProhibitedRule, AsteriskRequiredRule

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from unittest import mock

from boa_restrictor.cli.configuration import is_rule_excluded, is_rule_excluded_per_file, load_configuration


@mock.patch.object(tomllib, "load", return_value={"tool": {"boa-restrictor": {"exclude": ["PBR001"]}}})
def test_load_configuration_exclusion_rules(mocked_load):
    data = load_configuration(file_path=os.path.abspath(sys.argv[0]))

    mocked_load.assert_called_once()
    assert data == {"exclude": ["PBR001"]}


@mock.patch.object(tomllib, "load", return_value={"tool": {"boa-restrictor": {"enable_django_rules": False}}})
def test_load_configuration_enable_django_rules_set(mocked_load):
    data = load_configuration(file_path=os.path.abspath(sys.argv[0]))

    mocked_load.assert_called_once()
    assert data == {"enable_django_rules": False}


@mock.patch.object(
    tomllib, "load", return_value={"tool": {"boa-restrictor": {"per-file-excludes": {"*/test/*": ["PBR001"]}}}}
)
def test_load_configuration_per_file_excludes(mocked_load):
    data = load_configuration(file_path=os.path.abspath(sys.argv[0]))

    mocked_load.assert_called_once()
    assert data == {"per-file-excludes": {"*/test/*": ["PBR001"]}}


@mock.patch.object(tomllib, "load")
def test_load_configuration_invalid_file(mocked_load):
    data = load_configuration(file_path="invalid_file.toml")

    mocked_load.assert_not_called()
    assert data == {}


@mock.patch.object(tomllib, "load", side_effect=tomllib.TOMLDecodeError)
def test_load_configuration_invalid_toml(mocked_load):
    filename = os.path.abspath(sys.argv[0])
    with pytest.raises(TomlParsingError, match=rf'TOML file "{re.escape(filename)}" contains syntax errors.'):
        load_configuration(file_path=filename)


@mock.patch.object(tomllib, "load", return_value={"tool": {"other_linter": True}})
def test_load_configuration_key_missing(mocked_load):
    data = load_configuration(file_path=os.path.abspath(sys.argv[0]))

    mocked_load.assert_called_once()
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
