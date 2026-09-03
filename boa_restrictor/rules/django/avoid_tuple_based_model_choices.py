import ast

from boa_restrictor.common.django_models import (
    find_model_field_aliases,
    find_model_module_aliases,
    is_django_model_class,
)
from boa_restrictor.common.file_detection import is_layer_file
from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class AvoidTupleBasedModelChoices(Rule):
    """
    Prohibit the usage of tuple-based choices in model fields.
    Use new class-based choices instead.

    Inside a model every tuple-of-pairs assignment counts; elsewhere only one whose name ends in "CHOICES",
    since a tuple of pairs is an ordinary data structure outside that context. A class counts as a model
    when it declares model fields, so a base class defined in another file does not hide it.

    Migrations are exempt: they are generated and out of the developer's hands.
    """

    # Constant for tuple-based choice validation
    CHOICE_TUPLE_LENGTH = 2

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}006"
    RULE_LABEL = "Avoid using old tuple-based Django model choices. Use class-based choices instead."

    def _is_tuple_based_choices(self, value: ast.AST) -> bool:
        """
        Detection of old tuple-based choices:
        - Either ast.Tuple / ast.List
        - Elements must each be ast.Tuple (e.g. ('A','Active'))
        """
        if isinstance(value, (ast.Tuple, ast.List)):
            # Ignore empty structures
            if not value.elts:
                return False
            # Check if each element is a 2-tuple
            for elt in value.elts:
                if not (isinstance(elt, ast.Tuple) and len(elt.elts) == self.CHOICE_TUPLE_LENGTH):
                    return False
            return True
        return False

    def _is_choices_variable_name(self, target_name: str) -> bool:
        """
        Check if variable name suggests it contains choices (ends with 'CHOICES')
        """
        return target_name.upper().endswith("CHOICES")

    def _create_occurrence(self, line_number: int) -> Occurrence:
        """Create an occurrence for a tuple-based choices violation."""
        return Occurrence(
            filename=self.filename,
            file_path=self.file_path,
            rule_label=self.RULE_LABEL,
            rule_id=self.RULE_ID,
            line_number=line_number,
            identifier=None,
        )

    def check(self) -> list[Occurrence]:  # noqa: C901
        if is_layer_file(self.file_path, layer="migrations"):
            return []

        occurrences: list[Occurrence] = []

        field_aliases = find_model_field_aliases(self.source_tree)
        module_aliases = find_model_module_aliases(self.source_tree)

        # First pass: check assignments inside Django model classes
        django_model_assignments: set[int] = set()
        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.ClassDef) and is_django_model_class(
                node, field_aliases=field_aliases, module_aliases=module_aliases
            ):
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        django_model_assignments.add(id(stmt))
                        if self._is_tuple_based_choices(stmt.value):
                            occurrences.append(self._create_occurrence(stmt.lineno))

        # Second pass: check tuple-based choices assignments outside of Django models
        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.Assign) and id(node) not in django_model_assignments:
                if self._is_tuple_based_choices(node.value):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and self._is_choices_variable_name(target.id):
                            # Report the line number of the first tuple element for better user experience
                            line_number = node.value.elts[0].lineno if node.value.elts else node.lineno
                            occurrences.append(self._create_occurrence(line_number))

        return occurrences
