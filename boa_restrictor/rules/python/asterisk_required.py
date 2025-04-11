import ast

from boa_restrictor.common.rule import PYTHON_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class AsteriskRequiredRule(Rule):
    """
    Checks if a method or function contains positional arguments (missing leading "*")
    "self" and "cls" are allowlisted, even if they are used outside a class context.
    """

    RULE_ID = f"{PYTHON_LINTING_RULE_PREFIX}001"
    RULE_LABEL = 'Positional arguments in functions and methods are discouraged. Add an "*" as the first argument.'

    def _missing_asterisk(self, *, node) -> bool:
        for arg in node.args.args:
            if isinstance(arg, ast.arg) and arg.arg not in ("self", "cls"):
                return True

        return False

    def check(self) -> list[Occurrence]:
        occurrences = []

        for node in ast.walk(self.source_tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if self._missing_asterisk(node=node):
                occurrences.append(
                    Occurrence(
                        rule_id=self.RULE_ID,
                        rule_label=self.RULE_LABEL,
                        filename=self.filename,
                        identifier=node.name,
                        line_number=node.lineno,
                    )
                )

        return occurrences
