import importlib
import inspect
from pathlib import Path

from boa_restrictor.common.rule import Rule
from boa_restrictor.rules import BOA_RESTRICTOR_RULES, DJANGO_BOA_RULES, get_rules


def _concrete_rule_classes_on_disk() -> set[type[Rule]]:
    """
    Discovers every concrete rule defined in the rules packages. Abstract base rules (which omit a
    "RULE_ID") are excluded, as they are not meant to be registered themselves.
    """
    rules_root = Path(__file__).resolve().parent.parent.parent / "boa_restrictor" / "rules"
    classes: set[type[Rule]] = set()

    for package in ("python", "django"):
        for file in (rules_root / package).iterdir():
            if file.suffix != ".py" or file.name == "__init__.py":
                continue

            module = importlib.import_module(f"boa_restrictor.rules.{package}.{file.stem}")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                # Only count rules defined in this very module that declare a concrete RULE_ID.
                if issubclass(obj, Rule) and obj.__module__ == module.__name__ and "RULE_ID" in vars(obj):
                    classes.add(obj)

    return classes


def test_boa_restrictor_rules_constant_not_missing_rules():
    """
    This test is a check to ensure we don't forget to register new rules.
    """
    assert _concrete_rule_classes_on_disk() == set(get_rules(use_django_rules=True))


def test_get_rules_django_rules_enabled():
    assert get_rules(use_django_rules=True) == BOA_RESTRICTOR_RULES + DJANGO_BOA_RULES


def test_get_rules_django_rules_disabled():
    assert get_rules(use_django_rules=False) == BOA_RESTRICTOR_RULES
