import ast

from boa_restrictor.common.rule import LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class DataclassWithKwargsOnlyRule(Rule):
    """
    This rule will enforce that you use the `kw_only` parameter in every dataclass decorator.
    This will force the developer to set all dataclass attributes as kwargs instead of args, which is more explicit and
    easier to refactor.
    """

    RULE_ID = f"{LINTING_RULE_PREFIX}004"
    RULE_LABEL = 'Enforces "kw_only" parameter in dataclass decorator.'

    def check(self) -> list[Occurrence]:
        occurrences = []

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.ClassDef):
                for decorator in node.decorator_list:
                    if (
                        (
                            isinstance(decorator, ast.Call)
                            and (
                                (isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass")
                                or (isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "dataclass")
                            )
                        )
                        or (isinstance(decorator, ast.Name) and decorator.id == "dataclass")
                        or (isinstance(decorator, ast.Attribute) and decorator.attr == "dataclass")
                    ):
                        # We use the default that "kw_only" is absent
                        kw_only_present = False
                        if isinstance(decorator, ast.Call):
                            kw_only_present = any(
                                isinstance(arg, ast.keyword) and arg.arg == "kw_only" and arg.value.value is True
                                for arg in decorator.keywords
                            )
                        if not kw_only_present:
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
