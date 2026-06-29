import ast

from boa_restrictor.common.file_detection import is_test_file
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

        if not is_test_file(self.file_path):
            return occurrences

        for node in ast.walk(self.source_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                if self._contains_loop_or_comprehension(node):
                    occurrences.append(self._build_occurrence(line_number=node.lineno, identifier=node.name))

        return occurrences

    def _contains_loop_or_comprehension(self, node) -> bool:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.ListComp, ast.SetComp, ast.DictComp)):
                return True
            if self._contains_loop_or_comprehension(child):
                return True
        return False
