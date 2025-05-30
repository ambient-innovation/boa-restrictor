import ast

from boa_restrictor.common.rule import PYTHON_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class AvoidTypeHintsInVariableNamesAsSuffix(Rule):
    """
    This rule will enforce that variables don't contain type hints as suffixes like "user_list" or "project_qs".
    """

    RULE_ID = f"{PYTHON_LINTING_RULE_PREFIX}007"
    RULE_LABEL = "Prohibit type-hinting in variable names"

    BAD_SUFFIXES = ("_list", "_dict", "_set", "_str", "_int", "_float", "_bool", "_qs")

    def check(self) -> list[Occurrence]:  # noqa: C901
        occurrences = []

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if not isinstance(target, ast.Name):
                        continue
                    var_name = target.id
                    for suffix in self.BAD_SUFFIXES:
                        if var_name.endswith(suffix):
                            occurrences.append(
                                Occurrence(
                                    rule_id=self.RULE_ID,
                                    rule_label=self.RULE_LABEL,
                                    filename=self.filename,
                                    file_path=self.file_path,
                                    identifier=var_name,
                                    line_number=node.lineno,
                                )
                            )
            # For type annotations
            elif isinstance(node, ast.AnnAssign):
                if not isinstance(node.target, ast.Name):
                    continue
                var_name = node.target.id
                for suffix in self.BAD_SUFFIXES:
                    if var_name.endswith(suffix):
                        occurrences.append(
                            Occurrence(
                                rule_id=self.RULE_ID,
                                rule_label=self.RULE_LABEL,
                                filename=self.filename,
                                file_path=self.file_path,
                                identifier=var_name,
                                line_number=node.lineno,
                            )
                        )

        return occurrences
