from pathlib import Path

from boa_restrictor.rules import BOA_RESTRICTOR_RULES, DJANGO_BOA_RULES, get_rules


def test_boa_restrictor_rules_constant_not_missing_rules():
    """
    This test is a check to ensure we don't forget to register new rules.
    """
    number_of_rule_files = 0

    # Python rules
    for file in (Path(__file__).resolve().parent.parent.parent / "boa_restrictor/rules/python").iterdir():
        if file.suffix == ".py" and file.name != "__init__.py":
            number_of_rule_files += 1

    # Django rules
    for file in (Path(__file__).resolve().parent.parent.parent / "boa_restrictor/rules/django").iterdir():
        if file.suffix == ".py" and file.name != "__init__.py":
            number_of_rule_files += 1

    assert len(get_rules(use_django_rules=True)) == number_of_rule_files


def test_get_rules_django_rules_enabled():
    assert get_rules(use_django_rules=True) == BOA_RESTRICTOR_RULES + DJANGO_BOA_RULES


def test_get_rules_django_rules_disabled():
    assert get_rules(use_django_rules=False) == BOA_RESTRICTOR_RULES
