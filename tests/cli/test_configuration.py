import os
import sys
import warnings

from boa_restrictor.rules import AsteriskRequiredRule

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from unittest import mock

from boa_restrictor.cli.configuration import is_rule_excluded, is_rule_excluded_per_file, load_configuration


@mock.patch.object(tomllib, "load", return_value={"tool": {"boa-restrictor": {"exclude": ["PBR001"]}}})
def test_load_configuration_happy_path(mocked_load):
    data = load_configuration(file_path=os.path.abspath(sys.argv[0]))

    mocked_load.assert_called_once()
    assert data == {"exclude": ["PBR001"]}


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


@mock.patch.object(tomllib, "load", return_value={"tool": {"other_linter": True}})
def test_load_configuration_key_missing(mocked_load):
    data = load_configuration(file_path=os.path.abspath(sys.argv[0]))

    mocked_load.assert_called_once()
    assert data == {}


def test_is_rule_excluded_is_excluded():
    assert is_rule_excluded(rule_class=AsteriskRequiredRule, excluded_rules=["PBR001"]) is True


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
