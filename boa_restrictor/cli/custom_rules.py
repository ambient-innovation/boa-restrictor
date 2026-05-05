import importlib
import re
import sys
from pathlib import Path

from boa_restrictor.common.rule import RESERVED_RULE_ID_PREFIXES, Rule
from boa_restrictor.exceptions.custom_rules import (
    CustomRuleAttributeMissingError,
    CustomRuleInvalidRuleIdShapeError,
    CustomRuleInvalidRuleIdTypeError,
    CustomRuleInvalidRuleLabelTypeError,
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

# Mirrors the noqa parser's _CODE_PATTERN: a RULE_ID that doesn't match this shape
# can never be silenced via "# noqa:", so reject it at load time.
_RULE_ID_SHAPE = re.compile(r"^[A-Z]+\d+$")


def load_custom_rules(*, paths, anchor_dir: Path) -> tuple[type[Rule], ...]:
    """
    Import custom rule classes from a list of dotted paths (e.g. "myproject.linting.MyRule").

    `anchor_dir` is prepended to sys.path (insert at position 0) so the user's project modules
    become importable when boa-restrictor runs as an installed console script. Inserting at the
    front means project-local modules win over identically-named installed packages — that's
    the intended behaviour, since the user is linting their own project.

    The anchor is canonicalised with `Path.resolve()` so non-canonical inputs (e.g. paths
    containing "..") don't accumulate as duplicate sys.path entries on repeated invocations.
    """
    if not isinstance(paths, list):
        raise CustomRulesNotAListError
    for item in paths:
        if not isinstance(item, str):
            raise CustomRulePathNotAStringError(item)

    if not paths:
        return ()

    anchor_str = str(anchor_dir.resolve())
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

    _validate_rule_class(rule_attr=rule_attr, dotted_path=dotted_path)
    return rule_attr


def _validate_rule_class(*, rule_attr, dotted_path: str) -> None:
    if not isinstance(rule_attr, type):
        raise CustomRuleNotAClassError(dotted_path)
    if not issubclass(rule_attr, Rule):
        raise CustomRuleNotARuleSubclassError(dotted_path)
    if not getattr(rule_attr, "RULE_ID", None):
        raise CustomRuleMissingRuleIdError(dotted_path)
    if not isinstance(rule_attr.RULE_ID, str):
        raise CustomRuleInvalidRuleIdTypeError(dotted_path=dotted_path, value=rule_attr.RULE_ID)
    if not getattr(rule_attr, "RULE_LABEL", None):
        raise CustomRuleMissingRuleLabelError(dotted_path)
    if not isinstance(rule_attr.RULE_LABEL, str):
        raise CustomRuleInvalidRuleLabelTypeError(dotted_path=dotted_path, value=rule_attr.RULE_LABEL)
    if not _RULE_ID_SHAPE.match(rule_attr.RULE_ID):
        raise CustomRuleInvalidRuleIdShapeError(dotted_path=dotted_path, rule_id=rule_attr.RULE_ID)

    for prefix in RESERVED_RULE_ID_PREFIXES:
        if rule_attr.RULE_ID.startswith(prefix):
            raise CustomRuleReservedPrefixError(
                dotted_path=dotted_path,
                prefix=prefix,
                reserved_prefixes=RESERVED_RULE_ID_PREFIXES,
            )


def validate_unique_rule_ids(*, rules: tuple[type[Rule], ...]) -> None:
    """
    Ensure no two rules share a RULE_ID, naming all offenders if any clash.
    Collects every duplicate before raising so users see the full picture in one go,
    grouped by rule ID (a triple-clash reports as one line with three classes).
    """
    by_id: dict[str, list[type[Rule]]] = {}
    for rule in rules:
        by_id.setdefault(rule.RULE_ID, []).append(rule)

    clashes = {rule_id: classes for rule_id, classes in by_id.items() if len(classes) > 1}
    if clashes:
        raise DuplicateRuleIdError(clashes=clashes)
