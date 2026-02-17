import ast

from boa_restrictor.common.rule import PYTHON_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class ReturnStatementRequiresTypeHintRule(Rule):
    """
    This rule checks if a return statement is set, then a return type hint has to be defined.
    Doesn't match the case if there is no return statement but a type hint.
    """

    RULE_ID = f"{PYTHON_LINTING_RULE_PREFIX}002"
    RULE_LABEL = "Return statements require return type hint."

    @staticmethod
    def _walk_scope(node: ast.AST):
        """Walk AST nodes within the current scope, skipping nested function definitions."""
        for child in ast.iter_child_nodes(node):
            yield child
            if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield from ReturnStatementRequiresTypeHintRule._walk_scope(child)

    def check(self) -> list[Occurrence]:
        occurrences = []

        for node in ast.walk(self.source_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                has_return_statement = any(isinstance(child, ast.Return) for child in self._walk_scope(node))
                has_return_annotation = node.returns is not None

                if has_return_statement and not has_return_annotation:
                    occurrences.append(
                        Occurrence(
                            filename=self.filename,
                            file_path=self.file_path,
                            rule_label=self.RULE_LABEL,
                            rule_id=self.RULE_ID,
                            line_number=node.lineno,
                            identifier=node.name,
                        )
                    )

        return occurrences
