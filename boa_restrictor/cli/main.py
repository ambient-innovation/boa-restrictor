import argparse
import re
import sys
import tokenize
import tomllib
from collections.abc import Sequence
from io import StringIO
from pathlib import Path

from boa_restrictor.common.rule import LINTING_RULE_PREFIX
from boa_restrictor.rules.asterisk_required import AsteriskRequiredRule
from boa_restrictor.rules.return_type_hints import ReturnStatementRequiresTypeHintRule


def main(argv: Sequence[str] | None = None):
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

    load_configuration()

    # TODO: get them from somewhere else
    linter_classes = (
        AsteriskRequiredRule,
        ReturnStatementRequiresTypeHintRule,
    )
    occurrences = []

    excluded_rules = load_configuration(file_path=args.config).get("exclude", [])

    for filename in args.filenames[1:]:
        with open(filename) as f:
            source_code = f.read()
        noqa_tokens = get_noqa_comments(source_code=source_code)

        for linter_class in linter_classes:
            if linter_class.RULE_ID in excluded_rules:
                continue

            excluded_lines = {token[0] for token in noqa_tokens if linter_class.RULE_ID in token[1]}
            # Ensure that line exclusions are respected
            occurrences.extend(
                [
                    possible_occurrence
                    for possible_occurrence in linter_class.run_check(filename=filename, source_code=source_code)
                    if possible_occurrence.line_number not in excluded_lines
                ]
            )

    current_path = Path.cwd()

    # TODO: möchte ich die hier noch irgendwie sortieren?
    if any(occurrences):
        for occurrence in occurrences:
            sys.stdout.write(
                f'"{current_path / occurrence.filename}:{occurrence.line_number}": '
                f"({occurrence.rule_id}) {occurrence.rule_label}\n"
            )
        sys.stdout.write(f"Found {len(occurrences)} occurrence(s) in the codebase.\n")
    else:
        print("Aller Code so yeah!")

    return bool(any(occurrences))


def load_configuration(*, file_path: str = "pyproject.toml") -> dict:
    file_path = Path.cwd() / file_path
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return {}

    try:
        # TODO: das tuts nicht
        return data["tool"]["boa-restrictor"]
    except KeyError:
        return {}


def get_noqa_comments(*, source_code: str) -> list[tuple[int, str]]:
    noqa_statements = []

    tokens = tokenize.generate_tokens(StringIO(source_code).readline)
    pattern = re.compile(r"^#\snoqa:\s*.*?" + LINTING_RULE_PREFIX + r"\d{3}")

    for token in tokens:
        token_type, token_string, start, _, _ = token

        if token_type == tokenize.COMMENT and pattern.search(token_string):
            noqa_statements.append((start[0], token_string.strip()))

    return noqa_statements


# TODO: configure RTD webhook
# TODO: RUF100 löscht unsere PBR noqa's -> pyproject.toml lint.external
#  (https://docs.astral.sh/ruff/settings/#lint_extend-unsafe-fixes)
