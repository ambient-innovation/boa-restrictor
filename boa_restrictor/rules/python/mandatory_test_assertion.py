import ast

from boa_restrictor.common.file_detection import is_test_file
from boa_restrictor.common.rule import PYTHON_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence

# Calls to "pytest.<name>(...)" that act as assertions (typically used as context managers).
PYTEST_ASSERTION_HELPERS = frozenset({"raises", "warns", "deprecated_call"})


class MandatoryTestAssertionRule(Rule):
    """
    Ensures that every test function contains at least one assertion. A test that asserts nothing can never
    fail and therefore provides no protection against regressions.
    """

    RULE_ID = f"{PYTHON_LINTING_RULE_PREFIX}010"
    RULE_LABEL = "Every test must contain at least one assertion."

    def check(self) -> list[Occurrence]:
        occurrences = []

        if not is_test_file(self.file_path):
            return occurrences

        for node in ast.walk(self.source_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                if not self._contains_assertion(node):
                    occurrences.append(self._build_occurrence(line_number=node.lineno, identifier=node.name))

        return occurrences

    @staticmethod
    def _contains_assertion(function_node) -> bool:
        for node in ast.walk(function_node):
            # Bare "assert ..." statement
            if isinstance(node, ast.Assert):
                return True

            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute):
                    # Any assert-prefixed method call (e.g. self.assertEqual), or a pytest assertion helper
                    # used as a context manager (see PYTEST_ASSERTION_HELPERS).
                    if func.attr.startswith("assert"):
                        return True
                    if (
                        isinstance(func.value, ast.Name)
                        and func.value.id == "pytest"
                        and func.attr in PYTEST_ASSERTION_HELPERS
                    ):
                        return True
                # Directly imported assert-prefixed helper, e.g. assertQuerySetEqual
                elif isinstance(func, ast.Name) and func.id.startswith("assert"):
                    return True

        return False
