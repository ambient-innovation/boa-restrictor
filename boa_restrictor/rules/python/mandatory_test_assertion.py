import ast

from boa_restrictor.common.ast_utils import is_test_function
from boa_restrictor.common.file_detection import is_test_file
from boa_restrictor.common.rule import PYTHON_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence

# Calls to "pytest.<name>(...)" that act as assertions (typically used as context managers).
PYTEST_ASSERTION_HELPERS = frozenset({"raises", "warns", "deprecated_call"})

# Calls that unconditionally fail the test (unittest's self.fail, pytest.fail). A test whose only
# "check" is one of these inside an except-branch still asserts behaviour: it fails on the wrong path.
FAILURE_CALL_NAMES = frozenset({"fail"})


class MandatoryTestAssertionRule(Rule):
    """
    Ensures that every test function contains at least one assertion. A test that asserts nothing can never
    fail and therefore provides no protection against regressions.

    A call to ``self.fail()`` / ``pytest.fail()`` counts as an assertion: such a test can fail (e.g. on the
    wrong branch of a try/except) and therefore does protect against regressions.
    """

    RULE_ID = f"{PYTHON_LINTING_RULE_PREFIX}010"
    RULE_LABEL = "Every test must contain at least one assertion."

    def check(self) -> list[Occurrence]:
        occurrences = []

        if not is_test_file(self.file_path):
            return occurrences

        for node in ast.walk(self.source_tree):
            if is_test_function(node):
                if not self._contains_assertion(node):
                    occurrences.append(self._build_occurrence(line_number=node.lineno, identifier=node.name))

        return occurrences

    @classmethod
    def _contains_assertion(cls, node) -> bool:
        for child in ast.iter_child_nodes(node):
            # Don't descend into nested function definitions: an assertion that lives only inside an
            # (uncalled) nested helper does not make the enclosing test assert anything.
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if cls._is_assertion(child) or cls._contains_assertion(child):
                return True

        return False

    @staticmethod
    def _is_assertion(node) -> bool:
        # Bare "assert ..." statement
        if isinstance(node, ast.Assert):
            return True

        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                # Any assert-prefixed method call (e.g. self.assertEqual), a failure call (e.g. self.fail,
                # pytest.fail), or a pytest assertion helper used as a context manager (e.g. pytest.raises,
                # see PYTEST_ASSERTION_HELPERS).
                if func.attr.startswith("assert") or func.attr in FAILURE_CALL_NAMES:
                    return True
                if (
                    isinstance(func.value, ast.Name)
                    and func.value.id == "pytest"
                    and func.attr in PYTEST_ASSERTION_HELPERS
                ):
                    return True
            # Directly imported assert-prefixed helper (e.g. assertQuerySetEqual), failure call (e.g. "fail"
            # imported via "from pytest import fail") or pytest assertion helper (e.g. "raises" imported via
            # "from pytest import raises").
            elif isinstance(func, ast.Name) and (
                func.id.startswith("assert") or func.id in PYTEST_ASSERTION_HELPERS or func.id in FAILURE_CALL_NAMES
            ):
                return True

        return False
