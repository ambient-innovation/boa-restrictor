import ast

from boa_restrictor.common.django_models import (
    find_declared_field_calls,
    find_model_field_aliases,
    find_model_module_aliases,
    is_model_field_call,
)
from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence

CHAR_FIELD = "CharField"
CHAR_FIELDS = frozenset({CHAR_FIELD})
MAX_LENGTH_KEYWORD = "max_length"


class CharFieldMaxLengthRequiredRule(Rule):
    """
    CharField must have "max_length" set.
    Either set "max_length" or use "TextField" instead.

    A field is recognised from the call expression -- "models.CharField(...)", an aliased models module, or
    a "CharField(...)" imported from "django.db.models" -- so a model inheriting from a base class defined
    in another file is covered too. Only declarations count: a "CharField" typing a query expression
    creates no column.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}007"
    RULE_LABEL = 'CharField must have "max_length" set. Either set "max_length" or use "TextField" instead.'

    @staticmethod
    def _has_valid_max_length(node: ast.Call) -> bool:
        """
        Check if the Call node has a max_length keyword with a non-None value.
        """
        for keyword in node.keywords:
            # A "**kwargs" spread (arg is None) could carry max_length; don't flag what we can't see.
            if keyword.arg is None:
                return True
            if keyword.arg == MAX_LENGTH_KEYWORD:
                return not (isinstance(keyword.value, ast.Constant) and keyword.value.value is None)
        return False

    def check(self) -> list[Occurrence]:
        field_aliases = find_model_field_aliases(self.source_tree)
        module_aliases = find_model_module_aliases(self.source_tree)

        occurrences = [
            self._build_occurrence(line_number=node.lineno)
            for node in find_declared_field_calls(self.source_tree)
            if is_model_field_call(
                node, field_names=CHAR_FIELDS, field_aliases=field_aliases, module_aliases=module_aliases
            )
            and not self._has_valid_max_length(node)
        ]

        return sorted(occurrences, key=lambda occurrence: occurrence.line_number)
