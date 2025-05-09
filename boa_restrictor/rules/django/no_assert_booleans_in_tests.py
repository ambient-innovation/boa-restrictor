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

    def is_testcase_class(self, class_node):
        for base in class_node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr == "TestCase":
                    return True
            elif isinstance(base, ast.Name):
                if base.id == "TestCase":  # pragma: no cover (this line gets hit in every branch)
                    return True
        return False

    def check(self) -> list[Occurrence]:
        occurrences = []
        for node in ast.walk(self.source_tree):
            if not (isinstance(node, ast.ClassDef) and self.is_testcase_class(node)):
                continue
            for class_item in node.body:
                if not isinstance(class_item, ast.FunctionDef):
                    continue
                for subnode in ast.walk(class_item):
                    if not isinstance(subnode, ast.Call):
                        continue
                    func = subnode.func
                    if isinstance(func, ast.Attribute) and func.attr in {"assertTrue", "assertFalse"}:
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
