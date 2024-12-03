import ast

from boa_restrictor.common.rule import LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class ReturnStatementRequiresTypeHintRule(Rule):
    """
    write me
    """

    RULE_ID = f"{LINTING_RULE_PREFIX}002"
    RULE_LABEL = "Return statements require return type hint."

    def check(self, *, source_code: str) -> list[Occurrence]:
        # TODO: bau mich um
        try:
            tree = ast.parse(source_code)
            # TODO: das mache ich bei jeder regel. wäre das geiler, das nur einmal zu machen?
        except SyntaxError:
            # TODO: das klingt sinnvoll, wollen wir das?
            # Ungültiger Code kann nicht 'from datetime import datetime' enthalten
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "datetime":
                    for alias in node.names:
                        if alias.name == "datetime":
                            return True
        return False
