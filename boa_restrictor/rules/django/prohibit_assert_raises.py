import ast

from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class AssertRaisesProhibitedRule(Rule):
    """
    Ensures that TestCase.assertRaises() is never used since asserting an exception without the actual error
    message leads to false positives.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}001"
    RULE_LABEL = 'Use of "assertRaises()" is discouraged. Use "assertRaisesMessage()" instead.'

    def _check_occurrence_duplication(self, *, occurrences: list[Occurrence], filename: str, line_number: int) -> bool:
        match_already_found = False
        for occurrence in occurrences:
            if occurrence.filename == filename and occurrence.line_number == line_number:
                match_already_found = True
        return match_already_found

    def _check_direct_call(self, node) -> bool:
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "assertRaises":
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
                    return True

        return False

    def _check_context_manager(self, node) -> bool:
        for item in node.items:
            if isinstance(item.context_expr, ast.Call):
                func = item.context_expr.func
                if isinstance(func, ast.Attribute) and func.attr == "assertRaises":
                    if isinstance(func.value, ast.Name) and func.value.id == "self":
                        return True
        return False

    def check(self) -> list[Occurrence]:
        occurrences = []

        for node in ast.walk(self.source_tree):
            node_matched = False

            # Direct call: self.assertRaises(...)
            if isinstance(node, ast.Call):
                node_matched = self._check_direct_call(node=node)

            # Context Manager: with self.assertRaises(...)
            elif isinstance(node, ast.With):
                node_matched = self._check_context_manager(node=node)

            if not node_matched:
                continue
            match_already_found = self._check_occurrence_duplication(
                occurrences=occurrences, filename=self.filename, line_number=node.lineno
            )

            if not match_already_found:
                occurrences.append(
                    Occurrence(
                        filename=self.filename,
                        rule_label=self.RULE_LABEL,
                        rule_id=self.RULE_ID,
                        line_number=node.lineno,
                        identifier=None,
                    )
                )

        return occurrences
