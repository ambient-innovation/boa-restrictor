import ast

from boa_restrictor.common.file_detection import is_test_file
from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class NoObjectsCreateInTestsRule(Rule):
    """
    Prohibits creating model instances via "<Model>.objects.create()" in test files. Use model_bakery instead,
    so test data setup stays concise and required fields are populated automatically.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}011"
    RULE_LABEL = 'Do not use "<Model>.objects.create()" in tests. Use model_bakery instead.'

    def check(self) -> list[Occurrence]:
        occurrences = []

        if not is_test_file(self.file_path):
            return occurrences

        for node in ast.walk(self.source_tree):
            if not isinstance(node, ast.Call):
                continue

            func = node.func
            # Match "<anything>.objects.create(...)"
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "create"
                and isinstance(func.value, ast.Attribute)
                and func.value.attr == "objects"
            ):
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
