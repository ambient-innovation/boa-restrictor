from pathlib import Path

from boa_restrictor.rules import BOA_RESTRICTOR_RULES


def test_boa_restrictor_rules_constant_not_missing_rules():
    """
    This test is a check to ensure we don't forget to register new rules.
    """
    number_of_rule_files = 0
    for file in Path("../../boa_restrictor/rules").iterdir():
        if file.suffix == ".py" and file.name != "__init__.py":
            number_of_rule_files += 1

    assert len(BOA_RESTRICTOR_RULES) == number_of_rule_files
