import ast
from pathlib import Path

from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class NoDjangoDbImportInViewsRule(Rule):
    """
    Ensures that TestCase.assertRaises() is never used since asserting an exception without the actual error
    message leads to false positives.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}002"
    RULE_LABEL = "Do not import from django.db in the view layer."

    def is_view_file(self, path: Path) -> bool:
        path = path.resolve()

        # 1. views.py?
        if path.name == "views.py":
            return True

        # 2. Liegt in einem Verzeichnis namens "views"
        return "views" in {p.name for p in path.parents if p.is_dir()}

    def check(self) -> list[Occurrence]:
        occurrences = []

        if self.is_view_file(path=self.file_path):
            return occurrences

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("django.db"):
                    occurrences.append(
                        Occurrence(
                            filename=self.filename,
                            rule_label=self.RULE_LABEL,
                            rule_id=self.RULE_ID,
                            line_number=node.lineno,
                            identifier=None,
                        )
                    )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("django.db"):
                        occurrences.append(  # noqa:PERF401
                            Occurrence(
                                filename=self.filename,
                                rule_label=self.RULE_LABEL,
                                rule_id=self.RULE_ID,
                                line_number=node.lineno,
                                identifier=None,
                            )
                        )

        return occurrences
