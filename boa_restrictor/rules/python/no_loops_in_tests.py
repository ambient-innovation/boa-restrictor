import ast
from pathlib import Path

from boa_restrictor.common.rule import PYTHON_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class NoLoopsInTestsRule(Rule):
    """
    Prohibits loops in tests since tests should be as simple as possible.
    """

    RULE_ID = f"{PYTHON_LINTING_RULE_PREFIX}008"
    RULE_LABEL = "Using loops in unit-tests is discouraged."

    def check(self) -> list[Occurrence]:
        occurrences = []

        if not self._is_test_file(self.file_path):
            return occurrences

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
                if self._contains_loop_or_list_comprehension(node):
                    occurrences.append(
                        Occurrence(
                            rule_id=self.RULE_ID,
                            rule_label=self.RULE_LABEL,
                            filename=self.filename,
                            file_path=self.file_path,
                            identifier=node.name,
                            line_number=node.lineno,
                        )
                    )

        return occurrences

    @staticmethod
    def _is_test_file(filepath: Path) -> bool:
        return (
            any(part == "tests" for part in filepath.parts)
            and filepath.name.startswith("test_")
            and filepath.name.endswith(".py")
        )

    def _contains_loop_or_list_comprehension(self, node) -> bool:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.ListComp)):
                return True
            if self._contains_loop_or_list_comprehension(child):
                return True
        return False
