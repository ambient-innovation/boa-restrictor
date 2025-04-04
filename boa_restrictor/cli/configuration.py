import fnmatch
import re
import sys
import warnings
from typing import Union

from boa_restrictor.common.rule import Rule
from boa_restrictor.rules import BOA_RESTRICTOR_RULES

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from pathlib import Path


def load_configuration(*, file_path: Union[Path, str] = "pyproject.toml") -> dict:
    """
    Load linter configuration from pyproject.toml file.
    """
    file_path = Path.cwd() / file_path
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return {}

    try:
        return data["tool"]["boa-restrictor"]
    except KeyError:
        return {}


def is_rule_excluded(*, rule_class: type[Rule], excluded_rules: list) -> bool:
    """
    Check if the given rule is in the exclusion list.
    """
    # Generate set of valid rules
    valid_rules = (rule_class.RULE_ID for rule_class in BOA_RESTRICTOR_RULES)

    # Check if the given rule is valid
    for invalid_configured_rule in [rule_id for rule_id in excluded_rules if rule_id not in valid_rules]:
        warnings.warn(
            f'Boa Restrictor: Invalid rule "{invalid_configured_rule}" in configuration detected.',
            category=UserWarning,
            stacklevel=2,
        )
        return False

    # Check if the given rule is in the exclusion list
    return rule_class.RULE_ID in excluded_rules


def is_rule_excluded_per_file(
    *, filename: str, rule_class: type[Rule], per_file_excluded_rules: dict[str, list]
) -> bool:
    """
    Check if the given rule is in the per-file-exclusion list.
    """
    # Iterate per-file rule exclusions
    for file_path_pattern in per_file_excluded_rules.keys():  # noqa: PLC0206
        # If the filename matches the pattern...
        if re.search(fnmatch.translate(file_path_pattern), filename):
            # Skip linters, which have been excluded for this file path pattern
            if is_rule_excluded(rule_class=rule_class, excluded_rules=per_file_excluded_rules[file_path_pattern]):
                return True
    return False
