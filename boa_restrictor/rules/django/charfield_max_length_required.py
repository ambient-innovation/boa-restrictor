import ast

from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class CharFieldMaxLengthRequiredRule(Rule):
    """
    CharField must have "max_length" set.
    Either set "max_length" or use "TextField" instead.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}007"
    RULE_LABEL = 'CharField must have "max_length" set. Either set "max_length" or use "TextField" instead.'

    def _is_django_model(self, node: ast.ClassDef) -> bool:
        """
        Check if a class inherits from models.Model (directly)
        """
        for base in node.bases:
            # models.Model
            if (
                isinstance(base, ast.Attribute)
                and base.attr == "Model"
                and isinstance(base.value, ast.Name)
                and base.value.id == "models"
            ):
                return True
            # or direct Model
            if isinstance(base, ast.Name) and base.id == "Model":
                return True
        return False

    def _is_charfield_call(self, node: ast.Call) -> bool:
        """
        Check if a Call node is models.CharField(...) or CharField(...)
        """
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "CharField"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "models"
        ):
            return True
        if isinstance(node.func, ast.Name) and node.func.id == "CharField":
            return True
        return False

    def _has_valid_max_length(self, node: ast.Call) -> bool:
        """
        Check if the Call node has a max_length keyword with a non-None value.
        """
        for keyword in node.keywords:
            if keyword.arg == "max_length":
                if isinstance(keyword.value, ast.Constant) and keyword.value.value is None:
                    return False
                return True
        return False

    def check(self) -> list[Occurrence]:
        occurrences: list[Occurrence] = []

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.ClassDef) and self._is_django_model(node):
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Call) and self._is_charfield_call(stmt):
                        if not self._has_valid_max_length(stmt):
                            occurrences.append(
                                Occurrence(
                                    filename=self.filename,
                                    file_path=self.file_path,
                                    rule_label=self.RULE_LABEL,
                                    rule_id=self.RULE_ID,
                                    line_number=stmt.lineno,
                                    identifier=None,
                                )
                            )

        return occurrences
