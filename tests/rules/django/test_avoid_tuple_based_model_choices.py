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
        line_number=1,
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


def test_tuple_based_choices_in_model_with_unresolvable_base_found():
    """
    The base class lives in another file, so it cannot be resolved. The declared model field identifies
    the class as a model, which drops the "name must end in CHOICES" requirement.
    """
    source_tree = ast.parse("""class Invoice(CommonInfo):
    STATUS = (("a", "Active"), ("i", "Inactive"))
    reference = models.CharField(max_length=10)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_tuple_based_choices_with_aliased_models_module_found():
    source_tree = ast.parse("""from django.db import models as db_models


class Invoice(CommonInfo):
    STATUS = (("a", "Active"), ("i", "Inactive"))
    reference = db_models.CharField(max_length=10)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 5  # noqa: PLR2004


def test_tuple_in_plain_class_without_choices_name_not_detected():
    """A class declaring no model fields is not a model, so an ordinary tuple of pairs stays untouched."""
    source_tree = ast.parse("""class Config:
    STATUS = (("a", "Active"), ("i", "Inactive"))""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_tuple_in_serializer_without_choices_name_not_detected():
    """Serializer fields are not model fields, so the class does not read as a model."""
    source_tree = ast.parse("""class MySerializer(serializers.Serializer):
    STATUS = (("a", "Active"), ("i", "Inactive"))
    name = serializers.CharField()""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_migration_file_is_ignored():
    source_tree = ast.parse("""class Migration(migrations.Migration):
    dependencies = (
        ('app', '0001_initial'),
        ('other', '0002_x'),
    )
    operations = [migrations.AddField(field=models.CharField(max_length=10))]""")

    occurrences = AvoidTupleBasedModelChoices.run_check(
        file_path=Path("/path/to/app/migrations/0002_auto.py"), source_tree=source_tree
    )

    assert occurrences == []


def test_tuple_in_non_model_class_with_field_call_in_method_ok():
    """A field call inside a method declares no column, so the class is no model."""
    source_tree = ast.parse("""class FieldFactory:
    DEFAULTS = (
        ('a', 'A'),
        ('b', 'B'),
    )

    def build(self):
        return models.CharField(max_length=10)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_tuple_based_choices_in_model_with_only_relation_fields_found():
    source_tree = ast.parse("""class Membership(CommonInfo):
    STATUS = (
        ('a', 'A'),
        ('b', 'B'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_tuple_in_query_expression_class_ok():
    """An "output_field" types a query expression, so a "Func" subclass is no model."""
    source_tree = ast.parse("""class ConcatName(models.Func):
    output_field = models.CharField()
    LOOKUP = (
        ('a', 1),
        ('b', 2),
    )""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_line_number_anchors_on_the_assignment_inside_a_model():
    """Both passes anchor on the assignment, so a "# noqa: DBR006" always belongs on that line."""
    source_tree = ast.parse("""class Invoice(CommonInfo):
    reference = models.CharField(max_length=1)
    STATUS_CHOICES = (
        ('a', 'A'),
        ('b', 'B'),
    )""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 3  # noqa: PLR2004


def test_line_number_anchors_on_the_assignment_outside_a_model():
    source_tree = ast.parse("""STATUS_CHOICES = (
    ('a', 'A'),
    ('b', 'B'),
)""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 1


def test_tuple_based_choices_in_model_inheriting_a_base_from_the_same_file_found():
    source_tree = ast.parse("""class CommonInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class Invoice(CommonInfo):
    STATUS = (
        ('a', 'A'),
        ('b', 'B'),
    )""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 6  # noqa: PLR2004


def test_tuple_in_class_inheriting_a_non_model_base_from_the_same_file_ok():
    source_tree = ast.parse("""class Mixin:
    LABEL = 'x'


class Config(Mixin):
    STATUS = (
        ('a', 'A'),
        ('b', 'B'),
    )""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_occurrences_are_sorted_by_line_number():
    source_tree = ast.parse("""TOP_CHOICES = (('a', 'A'), ('b', 'B'))


class MyModel(models.Model):
    STATUS = (('a', 'A'), ('b', 'B'))


BOTTOM_CHOICES = (('a', 'A'), ('b', 'B'))""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert [occurrence.line_number for occurrence in occurrences] == [1, 5, 8]


def test_chained_assignment_is_reported_once():
    source_tree = ast.parse("""STATUS_CHOICES = PRIORITY_CHOICES = (('a', 'A'), ('b', 'B'))""")

    occurrences = AvoidTupleBasedModelChoices.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 1
