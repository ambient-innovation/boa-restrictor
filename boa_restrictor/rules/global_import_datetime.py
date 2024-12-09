import ast

from boa_restrictor.common.rule import LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class GlobalImportDatetimeRule(Rule):
    """
    Checks if the "datetime" object was imported from the "datetime" module.
    This will lead to unclear and inconsistent code. Thus, we enforce a single way of using the datetime module.
    """

    RULE_ID = f"{LINTING_RULE_PREFIX}003"
    RULE_LABEL = "Prohibiting nested import of datetime from datetime module."

    def check(self) -> list[Occurrence]:
        occurrences = []

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "datetime":
                    occurrences.append(
                        Occurrence(
                            filename=self.filename,
                            rule_label=self.RULE_LABEL,
                            rule_id=self.RULE_ID,
                            line_number=node.lineno,
                            function_name=None,
                        )
                    )

        return occurrences
