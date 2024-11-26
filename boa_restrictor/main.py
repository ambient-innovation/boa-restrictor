# todo: add exclusion rules for linting (pyproject.toml + noqa
import argparse
import re
import sys
from pathlib import Path
from typing import Sequence

from boa_restrictor.projections.occurrence import Occurrence
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

    def _parse_inline_ignores(self, line):
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

    # todo: register checks dynamically depending on configured rules
    # rules = {"RULE_001": rule_001, "RULE_002": rule_002}
    # linter = CustomLinter(rules)

    linter_classes = (AsteriskRequiredRule,)
    occurrences = []
    for filename in args.filenames[1:]:
        for linter_class in linter_classes:
            occurrences.extend(linter_class.run_check(filename))

    return occurrences


if __name__ == "__main__":

    results = main()

    current_path = Path.cwd()

    if any(results):
        for occurrence in results:
            print(
                f"\"{current_path / occurrence.filename}:{occurrence.line_number}\": ({occurrence.rule_id}) {occurrence.rule_label}")
    else:
        print("Alle Funktionen so yeah!")

    sys.exit(int(any(results)))
