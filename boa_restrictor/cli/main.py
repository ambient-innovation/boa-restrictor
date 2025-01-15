import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from boa_restrictor.cli.configuration import is_rule_excluded, is_rule_excluded_per_file, load_configuration
from boa_restrictor.cli.utils import parse_source_code_or_fail
from boa_restrictor.common.noqa import get_noqa_comments
from boa_restrictor.rules import BOA_RESTRICTOR_RULES


def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(
        prog="boa-restrictor",
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames to process.",
    )
    parser.add_argument(
        "--config",
        default="pyproject.toml",
        type=str,
        help="Location of pyproject.toml configuration file",
    )
    args = parser.parse_args(argv)

    # Get excluded linting rules from configuration
    globally_excluded_rules = load_configuration(file_path=args.config).get("exclude", [])
    per_file_excluded_rules: dict[str, list[str]] = load_configuration(file_path=args.config).get(
        "per-file-excludes", {}
    )

    # Iterate over all filenames coming from pre-commit...
    occurrences = []
    for filename in args.filenames[1:]:
        # Read source code
        with open(filename) as f:
            source_code = f.read()

        # Parse code through abstract syntax tree
        source_tree = parse_source_code_or_fail(filename=filename, source_code=source_code)

        # Fetch all ignored line comments
        noqa_tokens = get_noqa_comments(source_code=source_code)

        # Iterate over all linters...
        for rule_class in BOA_RESTRICTOR_RULES:
            # Skip linters, which have been excluded globally via the configuration
            if is_rule_excluded(rule_class=rule_class, excluded_rules=globally_excluded_rules):
                continue

            # Iterate per-file rule exclusions
            if is_rule_excluded_per_file(
                filename=filename, rule_class=rule_class, per_file_excluded_rules=per_file_excluded_rules
            ):
                continue

            # Ensure that line exclusions are respected
            excluded_lines = {token[0] for token in noqa_tokens if rule_class.RULE_ID in token[1]}

            # Add issues to our occurrence list
            occurrences.extend(
                [
                    possible_occurrence
                    for possible_occurrence in rule_class.run_check(filename=filename, source_tree=source_tree)
                    if possible_occurrence.line_number not in excluded_lines
                ]
            )

    # If we have any matches...
    if any(occurrences):
        current_path = Path.cwd()

        # Iterate over them and print details for the user
        for occurrence in occurrences:
            sys.stdout.write(
                f'"{current_path / occurrence.filename}:{occurrence.line_number}": '
                f"({occurrence.rule_id}) {occurrence.rule_label}\n"
            )

    # Since pre-commit will run this function x times, we skip any success or result count messages.

    return bool(any(occurrences))
