import ast
from pathlib import Path

from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class NoDjangoDbImportInViewsRule(Rule):
    """
    Ensures that no Django low-level database functionality is imported and therefore used in the view layer.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}002"
    RULE_LABEL = 'Do not use "django.db" in the view layer. Move it to a manager instead.'

    def is_view_file(self, path: Path) -> bool:
        path = path.resolve()

        if path.name == "views.py":
            return True

        return "views" in path.parts

    def check(self) -> list[Occurrence]:
        occurrences = []

        if not self.is_view_file(path=self.file_path):
            return occurrences

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("django.db") or (
                    module == "django" and any(alias.name == "db" for alias in node.names)
                ):
                    occurrences.append(
                        Occurrence(
                            filename=self.filename,
                            file_path=self.file_path,
                            rule_label=self.RULE_LABEL,
                            rule_id=self.RULE_ID,
                            line_number=node.lineno,
                            identifier=None,
                        )
                    )

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("django.db"):
                        occurrences.append(  # noqa: PERF401
                            Occurrence(
                                filename=self.filename,
                                file_path=self.file_path,
                                rule_label=self.RULE_LABEL,
                                rule_id=self.RULE_ID,
                                line_number=node.lineno,
                                identifier=None,
                            )
                        )

        return occurrences
