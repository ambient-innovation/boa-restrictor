import ast

from boa_restrictor.common.rule import LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class ReturnStatementRequiresTypeHintRule(Rule):
    """
    This rule checks if a return statement is set, then a return type hint has to be defined.
    Doesn't match the case if there is no return statement but a type hint.
    """

    RULE_ID = f"{LINTING_RULE_PREFIX}002"
    RULE_LABEL = "Return statements require return type hint."

    def check(self) -> list[Occurrence]:
        occurrences = []

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.FunctionDef):
                has_return_statement = any(isinstance(child, ast.Return) for child in ast.walk(node))
                has_return_annotation = node.returns is not None

                if has_return_statement and not has_return_annotation:
                    occurrences.append(
                        Occurrence(
                            filename=self.filename,
                            rule_label=self.RULE_LABEL,
                            rule_id=self.RULE_ID,
                            line_number=node.lineno,
                            identifier=node.name,
                        )
                    )

        return occurrences
