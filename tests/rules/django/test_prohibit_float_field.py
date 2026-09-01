import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.django.prohibit_float_field import ProhibitFloatFieldRule


def test_float_field_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    amount = models.FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="file.py",
        file_path=Path("/path/to/file.py"),
        line_number=2,
        rule_id=ProhibitFloatFieldRule.RULE_ID,
        rule_label=ProhibitFloatFieldRule.RULE_LABEL,
        identifier="FloatField",
    )


def test_float_field_in_model_with_unresolvable_base_found():
    """
    The base class lives in another file, so the linter cannot tell that this is a model. The qualified
    "models.FloatField" spelling is proof enough on its own.
    """
    source_tree = ast.parse("""class Invoice(CommonInfo):
    amount = models.FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_fully_qualified_float_field_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    amount = django.db.models.FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_directly_imported_float_field_found():
    source_tree = ast.parse("""from django.db.models import FloatField


class MyModel(models.Model):
    amount = FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 5  # noqa: PLR2004


def test_aliased_float_field_import_found():
    source_tree = ast.parse("""from django.db.models import FloatField as Float


class MyModel(models.Model):
    amount = Float()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 5  # noqa: PLR2004


def test_bare_float_field_without_models_import_ok():
    """Without an import from "django.db.models", a bare "FloatField()" is some other class entirely."""
    source_tree = ast.parse("""from wtforms.fields import FloatField


class MyForm:
    amount = FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_serializer_float_field_ok():
    source_tree = ast.parse("""class MySerializer(serializers.Serializer):
    amount = serializers.FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_form_float_field_ok():
    source_tree = ast.parse("""class MyForm(forms.Form):
    amount = forms.FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_decimal_field_ok():
    source_tree = ast.parse("""class MyModel(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_annotated_float_field_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    amount: models.FloatField = models.FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_multiple_float_fields_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    amount = models.FloatField()
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    discount = models.FloatField(null=True)""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 2  # noqa: PLR2004
    assert {occurrence.line_number for occurrence in occurrences} == {2, 4}


def test_float_field_outside_class_found():
    source_tree = ast.parse("""amount = models.FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 1


def test_migration_file_is_ignored():
    source_tree = ast.parse("""amount = models.FloatField()""")

    occurrences = ProhibitFloatFieldRule.run_check(
        file_path=Path("/path/to/app/migrations/0001_initial.py"), source_tree=source_tree
    )

    assert occurrences == []


def test_no_float_field_ok():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(max_length=100)""")

    occurrences = ProhibitFloatFieldRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []
