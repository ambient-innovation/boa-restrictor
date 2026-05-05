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
    ThirdRuleClashingWithSample,
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


def test_load_custom_rules_anchor_canonicalised_for_dedup(tmp_path):
    """Non-canonical anchors (containing '..') must dedup against the resolved form,
    so repeated invocations don't accumulate duplicate sys.path entries."""
    sub = tmp_path / "sub"
    sub.mkdir()
    canonical = str(tmp_path.resolve())
    sys.path.insert(0, canonical)
    sys_path_len_before = len(sys.path)

    # Pass a non-canonical form pointing at the same directory
    non_canonical = sub / ".."
    load_custom_rules(
        paths=[f"{FIXTURE_MODULE}.SampleCustomRule"],
        anchor_dir=non_canonical,
    )

    assert len(sys.path) == sys_path_len_before
    assert canonical in sys.path


def test_load_custom_rules_paths_must_be_list():
    with pytest.raises(CustomRuleConfigurationError, match=r"must be a list"):
        load_custom_rules(paths="myproject.MyRule", anchor_dir=Path.cwd())


def test_load_custom_rules_paths_must_contain_strings():
    with pytest.raises(CustomRuleConfigurationError, match=r"must be a string") as exc_info:
        load_custom_rules(paths=[123], anchor_dir=Path.cwd())

    # The offending value should be cited so users can find their typo
    assert "123" in str(exc_info.value)


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


def test_load_custom_rules_module_raises_non_import_error():
    """A custom rule module that raises e.g. RuntimeError (or Django's ImproperlyConfigured)
    at import time should still be re-framed as a CustomRuleImportError so users get an
    actionable message instead of a raw traceback."""
    with pytest.raises(CustomRuleImportError, match=r"Could not import module") as exc_info:
        load_custom_rules(
            paths=["tests.fixtures.raises_at_import.Anything"],
            anchor_dir=Path.cwd(),
        )

    # The original RuntimeError should chain via __cause__
    assert isinstance(exc_info.value.__cause__, RuntimeError)
    assert "simulated module-import-time failure" in str(exc_info.value.__cause__)


def test_load_custom_rules_syntax_error_message_is_specific(tmp_path):
    """A SyntaxError in the user's rule module should produce a syntax-specific hint
    rather than the generic "Make sure your project is on the Python path" message."""
    broken_module = tmp_path / "broken_rule.py"
    broken_module.write_text("def thing(:\n    pass\n")  # invalid syntax

    with pytest.raises(CustomRuleImportError) as exc_info:
        load_custom_rules(
            paths=["broken_rule.SomeRule"],
            anchor_dir=tmp_path,
        )

    message = str(exc_info.value)
    assert "Fix the syntax error" in message
    assert "Python path" not in message
    assert isinstance(exc_info.value.__cause__, SyntaxError)


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


def test_load_custom_rules_non_string_rule_id():
    """A non-string RULE_ID must raise a clean validation error rather than an AttributeError
    on the downstream str.startswith() check."""
    with pytest.raises(CustomRuleValidationError, match=r"non-string RULE_ID"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithNonStringRuleId"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_non_string_rule_label():
    with pytest.raises(CustomRuleValidationError, match=r"non-string RULE_LABEL"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithNonStringRuleLabel"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_lowercase_rule_id_rejected():
    """Lowercase RULE_IDs cannot be silenced via # noqa: (the noqa parser accepts only
    uppercase), so reject them at load time rather than letting them load and silently
    misbehave."""
    with pytest.raises(CustomRuleValidationError, match=r"malformed RULE_ID"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithLowercaseRuleId"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_punctuated_rule_id_rejected():
    with pytest.raises(CustomRuleValidationError, match=r"malformed RULE_ID"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithPunctuatedRuleId"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_letters_only_rule_id_rejected():
    """RULE_ID without any digits violates ^[A-Z]+\\d+$ and must be rejected."""
    with pytest.raises(CustomRuleValidationError, match=r"malformed RULE_ID"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithLettersOnlyRuleId"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_digits_only_rule_id_rejected():
    """RULE_ID without any letters violates ^[A-Z]+\\d+$ and must be rejected."""
    with pytest.raises(CustomRuleValidationError, match=r"malformed RULE_ID"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithDigitsOnlyRuleId"],
            anchor_dir=Path.cwd(),
        )


def test_load_custom_rules_trailing_letters_rule_id_rejected():
    """A letter after the digit run violates ^[A-Z]+\\d+$ and must be rejected."""
    with pytest.raises(CustomRuleValidationError, match=r"malformed RULE_ID"):
        load_custom_rules(
            paths=[f"{FIXTURE_MODULE}.RuleWithTrailingLettersRuleId"],
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


def test_validate_unique_rule_ids_reports_all_clashes_at_once():
    """A single error should list every duplicate so users do not have to fix-and-rerun repeatedly."""
    with pytest.raises(DuplicateRuleIdError) as exc_info:
        validate_unique_rule_ids(
            rules=(
                AsteriskRequiredRule,  # PBR001
                SampleCustomRule,  # TST001
                RuleCollidingWithBuiltin,  # PBR001 clash
                RuleClashingWithSample,  # TST001 clash
            )
        )

    message = str(exc_info.value)
    # Both clashes must appear in the same error message
    assert "PBR001" in message
    assert "TST001" in message
    assert "AsteriskRequiredRule" in message
    assert "SampleCustomRule" in message
    assert "RuleCollidingWithBuiltin" in message
    assert "RuleClashingWithSample" in message


def test_validate_unique_rule_ids_groups_triple_clash_on_one_line():
    """A triple-clash should report all three offenders under one rule-ID heading,
    not as three pairwise comparisons."""
    with pytest.raises(DuplicateRuleIdError) as exc_info:
        validate_unique_rule_ids(
            rules=(SampleCustomRule, RuleClashingWithSample, ThirdRuleClashingWithSample),
        )

    message = str(exc_info.value)
    # Exactly one line per clashing RULE_ID
    clash_lines = [line for line in message.splitlines() if line.strip().startswith("-")]
    assert len(clash_lines) == 1
    # All three offenders named on that single line
    assert "SampleCustomRule" in clash_lines[0]
    assert "RuleClashingWithSample" in clash_lines[0]
    assert "ThirdRuleClashingWithSample" in clash_lines[0]
