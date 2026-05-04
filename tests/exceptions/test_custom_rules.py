import pytest

from boa_restrictor.exceptions.custom_rules import (
    CustomRuleConfigurationError,
    CustomRuleError,
    CustomRuleImportError,
    CustomRuleValidationError,
    DuplicateRuleIdError,
)


@pytest.mark.parametrize(
    "exc_cls",
    [
        CustomRuleConfigurationError,
        CustomRuleImportError,
        CustomRuleValidationError,
        DuplicateRuleIdError,
    ],
)
def test_custom_rule_errors_inherit_from_base(exc_cls):
    assert issubclass(exc_cls, CustomRuleError)


def test_custom_rule_error_inherits_from_value_error():
    assert issubclass(CustomRuleError, ValueError)


def test_custom_rule_error_carries_message():
    with pytest.raises(CustomRuleError, match="boom"):
        raise CustomRuleError("boom")
