# todo: add exclusion rules for linting (pyproject.toml + noqa
import argparse
import re
import sys
import tokenize
from io import StringIO
from pathlib import Path
from typing import Sequence

from boa_restrictor.common.rule import LINTING_RULE_PREFIX
from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.projections.return_type_hints import ReturnStatementRequiresTypeHintRule
from boa_restrictor.rules.asterisk import AsteriskRequiredRule


class CustomLinter:
    def __init__(self, rules):
        self.rules = rules  # {rule_id: callable_rule_function}
        self.ignored_rules = set()

    def load_config(self, config_file):
        # Beispiel: Lade ausgeschlossene Regeln aus einer Konfigurationsdatei
        with open(config_file, 'r') as f:
            config = f.read()
        self.ignored_rules = set(config.splitlines())

    def lint_file(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

        for line_no, line in enumerate(lines, start=1):
            # Inline-Ausschlüsse verarbeiten
            ignored_for_line = self._parse_inline_ignores(line)
            for rule_id, rule_fn in self.rules.items():
                if rule_id not in self.ignored_rules and rule_id not in ignored_for_line:
                    rule_fn(line, line_no)

    def _parse_inline_ignores(self, line):  # noqa: BR002
        # todo: inline comments mit noqa
        match = re.search(r"# noqa: (.+)", line)
        if match:
            return set(match.group(1).split(","))
        return set()


def main(argv: Sequence[str] | None = None) -> list[Occurrence]:
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

    linter_classes = (AsteriskRequiredRule, ReturnStatementRequiresTypeHintRule,)
    occurrences = []
    for filename in args.filenames[1:]:
        for linter_class in linter_classes:
            occurrences.extend(linter_class.run_check(filename))

    return occurrences


def get_noqa_comments(source_code: str):
    # todo: call this once and pass to rules. maybe only the ones that apply?
    noqa_statements = []

    # Tokenize den Quellcode
    tokens = tokenize.generate_tokens(StringIO(source_code).readline)

    for token in tokens:
        token_type, token_string, start, _, _ = token

        # Prüfe, ob es ein Kommentar ist und ob es "noqa" enthält
        # todo: mit regex das hier variabler matchbar machen?
        if token_type == tokenize.COMMENT and f"# noqa: {LINTING_RULE_PREFIX}" in token_string:
            noqa_statements.append((start[0], token_string.strip()))

    return noqa_statements


if __name__ == "__main__":

    results = main()

    current_path = Path.cwd()

    # todo: möchte ich die hier noch irgendwie sortieren?
    if any(results):
        for occurrence in results:
            sys.stdout.write(
                f"\"{current_path / occurrence.filename}:{occurrence.line_number}\": ({occurrence.rule_id}) {occurrence.rule_label}\n")
    else:
        print("Aller Code so yeah!")

    sys.exit(int(any(results)))
