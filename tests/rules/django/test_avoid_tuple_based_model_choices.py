import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.django.avoid_tuple_based_model_choices import AvoidTupleBasedModelChoices


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


def test_direct_model_inheritance_found():
    """Test line 34: Direct Model inheritance (not models.Model)"""
    source_tree = ast.parse("""class MyModel(Model):
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
    )
    status = CharField(max_length=1, choices=STATUS_CHOICES)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_empty_tuple_not_detected():
    """Test line 46: Empty tuple/list structures should not be detected"""
    source_tree = ast.parse("""class MyModel(models.Model):
    STATUS_CHOICES = ()
    EMPTY_LIST = []
    status = models.CharField(max_length=1)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_tuple_assignment_without_choices_name_not_detected():
    """Test line 91->90: Tuple-based assignment that doesn't end with 'CHOICES' should not be detected"""
    source_tree = ast.parse("""SOME_TUPLES = (
    ('A', 'Active'),
    ('I', 'Inactive'),
)

class MyModel(models.Model):
    status = models.CharField(max_length=1)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_invalid_tuple_structure_not_detected():
    """Test case where tuple elements are not 2-tuples"""
    source_tree = ast.parse("""class MyModel(models.Model):
    INVALID_CHOICES = (
        ('A',),  # Only one element
        ('B', 'Beta', 'Extra'),  # Three elements
    )
    status = models.CharField(max_length=1)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0
