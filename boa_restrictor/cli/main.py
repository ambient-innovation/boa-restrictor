import argparse
import re
import sys
import tokenize
import tomllib
from io import StringIO
from pathlib import Path
from typing import Sequence

from boa_restrictor.common.rule import LINTING_RULE_PREFIX
from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.asterisk_required import AsteriskRequiredRule
from boa_restrictor.rules.return_type_hints import ReturnStatementRequiresTypeHintRule


class CustomLinter:
    def __init__(self, rules):
        self.rules = rules  # {rule_id: callable_rule_function}
        self.ignored_rules = set()

    def load_config(self, config_file):
        # Beispiel: Lade ausgeschlossene Regeln aus einer Konfigurationsdatei
        with open(config_file, 'r') as f:
            config = f.read()
        self.ignored_rules = set(config.splitlines())


def main(argv: Sequence[str] | None = None) -> list[Occurrence]:  # noqa: ASF, PBR001
    parser = argparse.ArgumentParser(
        prog='boa-restrictor',
    )
    parser.add_argument(
        'filenames',
        nargs='*',
        help='Filenames to process.',
    )

    args = parser.parse_args(argv)

    # todo: register (or better exclude) checks dynamically depending on configured rules
    # rules = {"RULE_001": rule_001, "RULE_002": rule_002}
    # linter = CustomLinter(rules)

    load_configuration()

    # todo: get them from somewhere else
    linter_classes = (AsteriskRequiredRule, ReturnStatementRequiresTypeHintRule,)
    occurrences = []

    excluded_rules = load_configuration().get("excluded", [])

    for filename in args.filenames[1:]:
        with open(filename, "r") as f:
            source_code = f.read()
        noqa_tokens = get_noqa_comments(source_code=source_code)

        for linter_class in linter_classes:
            if linter_class.RULE_ID in excluded_rules:
                continue

            excluded_lines = {token[0] for token in noqa_tokens if linter_class.RULE_ID in token[1]}
            # Ensure that line exclusions are respected
            occurrences.extend(
                [possible_occurrence for possible_occurrence in
                 linter_class.run_check(filename=filename, source_code=source_code) if
                 possible_occurrence.line_number not in excluded_lines])

    return occurrences


def load_configuration(*, file_path=None) -> dict:
    # todo: get this from pre-commit
    file_path = Path.cwd() / "../pyproject.toml"
    with open(file_path, "rb") as f:
        data = tomllib.load(f)

    try:
        return data["tool"]["boa-restrictor"]
    except KeyError:
        return {}


def get_noqa_comments(source_code: str) -> list[tuple[int, str]]:
    noqa_statements = []

    tokens = tokenize.generate_tokens(StringIO(source_code).readline)

    for token in tokens:
        token_type, token_string, start, _, _ = token

        if token_type == tokenize.COMMENT and re.search(r"^#\snoqa:\s*.*?" + LINTING_RULE_PREFIX + r"\d{3}", token_string):
            noqa_statements.append((start[0], token_string.strip()))

    return noqa_statements


if __name__ == "__main__":
    results = main()

    current_path = Path.cwd()

    # todo: möchte ich die hier noch irgendwie sortieren?
    if any(results):
        for occurrence in results:
            sys.stdout.write(
                f"\"{current_path / occurrence.filename}:{occurrence.line_number}\": "
                f"({occurrence.rule_id}) {occurrence.rule_label}\n")
    else:
        print("Aller Code so yeah!")

    sys.exit(int(any(results)))

# todo: configure RTD webhook