import ast

from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class ProhibitAssertBooleanInTests(Rule):
    """
    Prohibit the usage of "assertTrue" and "assertFalse" in Django unittests.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}003"
    RULE_LABEL = (
        'Do not use "assertTrue" or "assertFalse" in Django unittests. Use "assertIs(x, True)" or '
        '"assertIs(x, False)" instead.'
    )

    def check(self) -> list[Occurrence]:
        occurrences = []
        for node in ast.walk(self.source_tree):
            if not isinstance(node, ast.Call):
                continue

            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in {"assertTrue", "assertFalse"}:
                if isinstance(func.value, ast.Name) and func.value.id == "self":
                    occurrences.append(
                        Occurrence(
                            filename=self.filename,
                            file_path=self.file_path,
                            rule_label=self.RULE_LABEL,
                            rule_id=self.RULE_ID,
                            line_number=node.lineno,
                            identifier=None,
                        )
                    )

        return occurrences
