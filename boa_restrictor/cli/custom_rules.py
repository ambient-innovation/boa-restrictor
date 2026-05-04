import importlib
import sys
from pathlib import Path

from boa_restrictor.common.rule import RESERVED_RULE_ID_PREFIXES, Rule
from boa_restrictor.exceptions.custom_rules import (
    CustomRuleAttributeMissingError,
    CustomRuleMissingRuleIdError,
    CustomRuleMissingRuleLabelError,
    CustomRuleModuleImportFailedError,
    CustomRuleNotAClassError,
    CustomRuleNotARuleSubclassError,
    CustomRulePathNotAStringError,
    CustomRuleReservedPrefixError,
    CustomRulesNotAListError,
    DuplicateCustomRulePathError,
    DuplicateRuleIdError,
    InvalidCustomRulePathError,
)


def load_custom_rules(*, paths, anchor_dir: Path) -> tuple[type[Rule], ...]:
    """
    Import custom rule classes from a list of dotted paths (e.g. "myproject.linting.MyRule").

    `anchor_dir` is prepended to sys.path so the user's project modules become importable
    when boa-restrictor runs as an installed console script.
    """
    if not isinstance(paths, list):
        raise CustomRulesNotAListError
    for item in paths:
        if not isinstance(item, str):
            raise CustomRulePathNotAStringError(item)

    if not paths:
        return ()

    anchor_str = str(anchor_dir)
    if anchor_str not in sys.path:
        sys.path.insert(0, anchor_str)

    seen_paths: set[str] = set()
    rules: list[type[Rule]] = []
    for dotted_path in paths:
        if dotted_path in seen_paths:
            raise DuplicateCustomRulePathError(dotted_path)
        seen_paths.add(dotted_path)
        rules.append(_import_custom_rule(dotted_path=dotted_path))

    return tuple(rules)


def _import_custom_rule(*, dotted_path: str) -> type[Rule]:
    if "." not in dotted_path:
        raise InvalidCustomRulePathError(dotted_path)

    module_path, _, attr_name = dotted_path.rpartition(".")

    try:
        module = importlib.import_module(module_path)
    except Exception as e:
        raise CustomRuleModuleImportFailedError(module_path=module_path, dotted_path=dotted_path, original=e) from e

    try:
        rule_attr = getattr(module, attr_name)
    except AttributeError as e:
        raise CustomRuleAttributeMissingError(
            module_path=module_path, attr_name=attr_name, dotted_path=dotted_path
        ) from e

    if not isinstance(rule_attr, type):
        raise CustomRuleNotAClassError(dotted_path)
    if not issubclass(rule_attr, Rule):
        raise CustomRuleNotARuleSubclassError(dotted_path)
    if not getattr(rule_attr, "RULE_ID", None):
        raise CustomRuleMissingRuleIdError(dotted_path)
    if not getattr(rule_attr, "RULE_LABEL", None):
        raise CustomRuleMissingRuleLabelError(dotted_path)

    for prefix in RESERVED_RULE_ID_PREFIXES:
        if rule_attr.RULE_ID.startswith(prefix):
            raise CustomRuleReservedPrefixError(
                dotted_path=dotted_path,
                prefix=prefix,
                reserved_prefixes=RESERVED_RULE_ID_PREFIXES,
            )

    return rule_attr


def validate_unique_rule_ids(*, rules: tuple[type[Rule], ...]) -> None:
    """
    Ensure no two rules share a RULE_ID, naming all offenders if any clash.
    Collects every duplicate before raising so users see the full picture in one go.
    """
    seen: dict[str, type[Rule]] = {}
    clashes: list[tuple[str, type[Rule], type[Rule]]] = []
    for rule in rules:
        existing = seen.get(rule.RULE_ID)
        if existing is not None:
            clashes.append((rule.RULE_ID, existing, rule))
        else:
            seen[rule.RULE_ID] = rule

    if clashes:
        raise DuplicateRuleIdError(clashes=clashes)
