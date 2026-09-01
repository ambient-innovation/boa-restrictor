import ast

from boa_restrictor.common.django_models import find_model_field_aliases, is_model_field_call
from boa_restrictor.common.file_detection import is_layer_file
from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence

FLOAT_FIELD = "FloatField"


class ProhibitFloatFieldRule(Rule):
    """
    Prohibits "FloatField" on Django models. It maps to the database's inexact floating-point type, so a
    value can come back slightly different from the one that went in: sums drift by a cent and equality
    lookups stop matching. "DecimalField" stores exact values, and once rows exist the correction costs a
    migration plus a data audit.

    A quantity that is inexact by nature -- a measurement, a ratio, a coordinate -- is a legitimate float
    and belongs behind a "# noqa: DBR009". Making that float a deliberate choice instead of a default is
    the point of the rule.

    Migrations are exempt: they are generated and out of the developer's hands.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}009"
    RULE_LABEL = 'Avoid "FloatField" for values that must be exact. Use "DecimalField" instead.'

    def check(self) -> list[Occurrence]:
        if is_layer_file(self.file_path, layer="migrations"):
            return []

        field_aliases = find_model_field_aliases(self.source_tree)

        return [
            self._build_occurrence(line_number=node.lineno, identifier=FLOAT_FIELD)
            for node in ast.walk(self.source_tree)
            if isinstance(node, ast.Call)
            and is_model_field_call(node, field_names=frozenset({FLOAT_FIELD}), field_aliases=field_aliases)
        ]
