import ast

from boa_restrictor.common.rule import DJANGO_LINTING_RULE_PREFIX, Rule
from boa_restrictor.projections.occurrence import Occurrence


class AvoidTupleBasedModelChoices(Rule):
    """
    Prohibit the usage of tuple-based choices in model fields.
    Use new class-based choices instead.
    """

    # Constant for tuple-based choice validation
    CHOICE_TUPLE_LENGTH = 2

    RULE_ID = f"{DJANGO_LINTING_RULE_PREFIX}006"
    RULE_LABEL = "Avoid using old tuple-based Django model choices. Use class-based choices instead."

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

    def _check_django_model_assignments(self, occurrences: list[Occurrence]) -> set[int]:
        """Check assignments inside Django model classes and return set of processed assignment IDs."""
        django_model_assignments = set()

        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.ClassDef) and self._is_django_model(node):
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        django_model_assignments.add(id(stmt))
                        if self._is_tuple_based_choices(stmt.value):
                            occurrences.append(self._create_occurrence(stmt.lineno))

        return django_model_assignments

    def _check_standalone_assignments(self, occurrences: list[Occurrence], django_model_assignments: set[int]) -> None:
        """Check tuple-based choices assignments outside of Django models."""
        for node in ast.walk(self.source_tree):
            if isinstance(node, ast.Assign) and id(node) not in django_model_assignments:
                if self._is_tuple_based_choices(node.value):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and self._is_choices_variable_name(target.id):
                            # Report the line number of the first tuple element for better user experience
                            line_number = node.value.elts[0].lineno if node.value.elts else node.lineno
                            occurrences.append(self._create_occurrence(line_number))

    def check(self) -> list[Occurrence]:
        occurrences: list[Occurrence] = []

        # Check assignments inside Django models first
        django_model_assignments = self._check_django_model_assignments(occurrences)

        # Check standalone assignments outside of models
        self._check_standalone_assignments(occurrences, django_model_assignments)

        return occurrences
