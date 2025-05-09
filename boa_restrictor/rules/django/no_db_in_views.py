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

    def is_type_checking_if(self, node) -> bool:
        # if TYPE_CHECKING:
        if isinstance(node, ast.If):
            test = node.test
            # Case 1: TYPE_CHECKING
            if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
                return True
            # Case 2: typing.TYPE_CHECKING
            elif (
                isinstance(test, ast.Attribute)
                and isinstance(test.value, ast.Name)
                and test.value.id == "typing"
                and test.attr == "TYPE_CHECKING"
            ):
                return True
        return False

    def check(self) -> list[Occurrence]:
        occurrences = []
        type_checking_lines = set()

        if not self.is_view_file(path=self.file_path):
            return occurrences

        for node in ast.walk(self.source_tree):
            if self.is_type_checking_if(node):
                for inner in node.body:
                    for subnode in ast.walk(inner):
                        if isinstance(subnode, (ast.Import, ast.ImportFrom)):
                            type_checking_lines.add(subnode.lineno)

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if node.lineno not in type_checking_lines and alias.name.startswith("django.db"):
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
            elif isinstance(node, ast.ImportFrom):
                if node.lineno not in type_checking_lines and (
                    node.module.startswith("django.db")
                    or (node.module == "django" and any(alias.name == "db" for alias in node.names))
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

        return occurrences
