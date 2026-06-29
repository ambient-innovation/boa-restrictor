import ast

from boa_restrictor.common.file_detection import is_test_file
from boa_restrictor.common.rule import PYTHON_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class NoInlineImportInTestsRule(Rule):
    """
    Prohibits local/inline imports (imports nested inside a function) within test files. Imports belong at the
    top of the module so the test's dependencies are obvious at a glance.
    """

    RULE_ID = f"{PYTHON_LINTING_RULE_PREFIX}009"
    RULE_LABEL = "Do not use local/inline imports in test files. Move them to the top of the module."

    def check(self) -> list[Occurrence]:
        occurrences = []

        if not is_test_file(self.file_path):
            return occurrences

        self._collect(self.source_tree, in_function=False, occurrences=occurrences)

        return occurrences

    def _collect(self, node, *, in_function: bool, occurrences: list[Occurrence]) -> None:
        inside_function = in_function or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))

        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.If) and self._is_type_checking_guard(child):
                # Imports guarded by ``if TYPE_CHECKING:`` are never executed at runtime and exist solely for
                # annotations, so they impose no runtime dependency. Skip the guard's body, but keep checking the
                # ``else`` branch, which does run at runtime.
                for orelse_node in child.orelse:
                    if inside_function and isinstance(orelse_node, (ast.Import, ast.ImportFrom)):
                        occurrences.append(self._build_occurrence(line_number=orelse_node.lineno))
                    self._collect(orelse_node, in_function=inside_function, occurrences=occurrences)
                continue
            if inside_function and isinstance(child, (ast.Import, ast.ImportFrom)):
                occurrences.append(self._build_occurrence(line_number=child.lineno))
            self._collect(child, in_function=inside_function, occurrences=occurrences)

    @staticmethod
    def _is_type_checking_guard(node: ast.If) -> bool:
        test = node.test
        if isinstance(test, ast.Name):
            return test.id == "TYPE_CHECKING"
        if isinstance(test, ast.Attribute):
            return test.attr == "TYPE_CHECKING"
        return False
