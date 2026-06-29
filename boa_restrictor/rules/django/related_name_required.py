import ast

from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence

# Django model fields that create a reverse relation and therefore should declare an explicit related_name.
RELATION_FIELDS = frozenset({"ForeignKey", "OneToOneField", "ManyToManyField"})


class RelatedNameRequiredRule(Rule):
    """
    Ensures that relational model fields (ForeignKey, OneToOneField, ManyToManyField) declare an explicit
    "related_name". Relying on the auto-generated default ("<model>_set") makes reverse accessors implicit and
    easy to break when a model is renamed.
    """

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}012"
    RULE_LABEL = 'Relational model fields must declare an explicit "related_name".'

    def check(self) -> list[Occurrence]:
        occurrences = []

        # Migrations are generated and out of the developer's hands, so they are exempt.
        if "migrations" in self.file_path.parts:
            return occurrences

        for node in ast.walk(self.source_tree):
            if not isinstance(node, ast.Call):
                continue

            field_name = self._node_name(node.func)
            if field_name not in RELATION_FIELDS:
                continue

            keyword_names = {keyword.arg for keyword in node.keywords}
            # A "**kwargs" spread (arg is None) could contain related_name; don't flag what we can't see.
            if None in keyword_names:
                continue
            if "related_name" in keyword_names:
                continue

            occurrences.append(
                Occurrence(
                    filename=self.filename,
                    file_path=self.file_path,
                    rule_label=self.RULE_LABEL,
                    rule_id=self.RULE_ID,
                    line_number=node.lineno,
                    identifier=field_name,
                )
            )

        return occurrences

    @staticmethod
    def _node_name(node) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None
