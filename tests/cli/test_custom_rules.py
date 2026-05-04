import sys
from pathlib import Path

import pytest

from boa_restrictor.cli.custom_rules import load_custom_rules, validate_unique_rule_ids
from boa_restrictor.exceptions.custom_rules import (
    CustomRuleConfigurationError,
    CustomRuleImportError,
    CustomRuleValidationError,
    DuplicateRuleIdError,
)
from boa_restrictor.rules import AsteriskRequiredRule
from tests.fixtures.custom_rule_module import (
    AnotherCustomRule,
    RuleClashingWithSample,
    RuleCollidingWithBuiltin,
    SampleCustomRule,
)

FIXTURE_MODULE = "tests.fixtures.custom_rule_module"


@pytest.fixture(autouse=True)
def _restore_sys_path():
    original = list(sys.path)
    yield
    sys.path[:] = original


def test_load_custom_rules_empty_list():
    assert load_custom_rules(paths=[], anchor_dir=Path.cwd()) == ()


def test_load_custom_rules_happy_path():
    rules = load_custom_rules(
        paths=[f"{FIXTURE_MODULE}.SampleCustomRule"],
        anchor_dir=Path.cwd(),
    )
    assert rules == (SampleCustomRule,)


def test_load_custom_rules_multiple_in_order():
    rules = load_custom_rules(
        paths=[
            f"{FIXTURE_MODULE}.SampleCustomRule",
            f"{FIXTURE_MODULE}.AnotherCustomRule",
        ],
        anchor_dir=Path.cwd(),
    )
    assert rules == (SampleCustomRule, AnotherCustomRule)


def test_load_custom_rules_injects_anchor_into_sys_path(tmp_path):
    load_custom_rules(paths=[], anchor_dir=tmp_path)
    # Empty paths should not pollute sys.path
    assert str(tmp_path) not in sys.path


def test_load_custom_rules_anchor_inserted_when_paths_present(tmp_path):
    load_custom_rules(
        paths=[f"{FIXTURE_MODULE}.SampleCustomRule"],
        anchor_dir=tmp_path,
    )
    assert sys.path[0] == str(tmp_path)


def test_load_custom_rules_anchor_not_duplicated(tmp_path):
    sys.path.insert(0, str(tmp_path))
    sys_path_len_before = len(sys.path)
    load_custom_rules(
        paths=[f"{FIXTURE_MODULE}.SampleCustomRule"],
        anchor_dir=tmp_path,
    )
    assert len(sys.path) == sys_path_len_before


def test_load_custom_rules_paths_must_be_list():
    with pytest.raises(CustomRuleConfigurationError, match="must be a list"):
        load_custom_rules(paths="myproject.MyRule", anchor_dir=Path.cwd())


def test_load_custom_rules_paths_must_contain_strings():
    with pytest.raises(CustomRuleConfigurationError, match="must be a list"):
        load_custom_rules(paths=[123], anchor_dir=Path.cwd())


def test_load_custom_rules_duplicate_path():
    with pytest.raises(CustomRuleConfigurationError, match=r"Duplicate entry"):
        load_custom_rules(
            paths=[
                f"{FIXTURE_MODULE}.SampleCustomRule",
                f"{FIXTURE_MODULE}.SampleCustomRule",
            ],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_bad_path_no_dot():
    with pytest.raises(CustomRuleImportError, match=r'Expected a dotted path of the form "module.ClassName"'):
        load_custom_rules(paths=["just_a_name"], anchor_dir=Path.cwd())


def test_load_custom_rules_module_not_found():
    with pytest.raises(CustomRuleImportError, match=r"Could not import module"):
        load_custom_rules(paths=["nonexistent_pkg.SomeRule"], anchor_dir=Path.cwd())


def test_load_custom_rules_attr_not_found():
    with pytest.raises(CustomRuleImportError, match=r"has no attribute"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.DoesNotExist"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_not_a_class():
    with pytest.raises(CustomRuleValidationError, match=r"is not a class"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.not_a_class"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_not_a_rule_subclass():
    with pytest.raises(CustomRuleValidationError, match=r"must subclass"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.NotARuleSubclass"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_missing_rule_id():
    with pytest.raises(CustomRuleValidationError, match=r"does not set RULE_ID"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithoutRuleId"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_missing_rule_label():
    with pytest.raises(CustomRuleValidationError, match=r"does not set RULE_LABEL"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithoutRuleLabel"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_reserved_python_prefix():
    with pytest.raises(CustomRuleValidationError, match=r'reserved RULE_ID prefix "PBR"'):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithReservedPrefix"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_reserved_django_prefix():
    with pytest.raises(CustomRuleValidationError, match=r'reserved RULE_ID prefix "DBR"'):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithReservedDjangoPrefix"],
            anchor_dir=Path.cwd(),
        )


def test_validate_unique_rule_ids_happy_path():
    validate_unique_rule_ids(rules=(SampleCustomRule, AnotherCustomRule))


def test_validate_unique_rule_ids_duplicate_within_customs():
    with pytest.raises(DuplicateRuleIdError) as exc_info:
        validate_unique_rule_ids(rules=(SampleCustomRule, RuleClashingWithSample))

    message = str(exc_info.value)
    assert "TST001" in message
    assert "SampleCustomRule" in message
    assert "RuleClashingWithSample" in message


def test_validate_unique_rule_ids_duplicate_against_builtin():
    with pytest.raises(DuplicateRuleIdError) as exc_info:
        validate_unique_rule_ids(rules=(AsteriskRequiredRule, RuleCollidingWithBuiltin))

    message = str(exc_info.value)
    assert "PBR001" in message
    assert "AsteriskRequiredRule" in message
    assert "RuleCollidingWithBuiltin" in message
