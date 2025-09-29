import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import AvoidTupleBasedModelChoices


def test_tuple_based_choices_in_model_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="file.py",
        file_path=Path("/path/to/file.py"),
        line_number=2,
        rule_id=AvoidTupleBasedModelChoices.RULE_ID,
        rule_label=AvoidTupleBasedModelChoices.RULE_LABEL,
        identifier=None,
    )


def test_tuple_based_choices_outside_of_model_found():
    source_tree = ast.parse("""STATUS_CHOICES = (
    ('A', 'Active'),
    ('I', 'Inactive'),
)

class MyModel(models.Model):
    status = models.CharField(max_length=1, choices=STATUS)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="file.py",
        file_path=Path("/path/to/file.py"),
        line_number=2,
        rule_id=AvoidTupleBasedModelChoices.RULE_ID,
        rule_label=AvoidTupleBasedModelChoices.RULE_LABEL,
        identifier=None,
    )


def test_integer_choices_ok():
    source_tree = ast.parse("""class MyModel(models.Model):
    class StatusChoices(models.IntegerChoices):
        ACTIVE = 1, "Active"
        INACTIVE = 2, "Inactive"
        PENDING = 3, "Pending"

    status = models.IntegerField(choices=StatusChoices.choices)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_string_choices_ok():
    source_tree = ast.parse("""class MyModel(models.Model):
    class StatusChoices(models.StringChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        PENDING = "pending", "Pending"

    status = models.CharField(choices=StatusChoices.choices, max_length=20)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0
