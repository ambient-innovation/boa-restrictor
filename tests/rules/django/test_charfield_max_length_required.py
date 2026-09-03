import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.django.charfield_max_length_required import CharFieldMaxLengthRequiredRule


def test_charfield_without_max_length_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="file.py",
        file_path=Path("/path/to/file.py"),
        line_number=2,
        rule_id=CharFieldMaxLengthRequiredRule.RULE_ID,
        rule_label=CharFieldMaxLengthRequiredRule.RULE_LABEL,
        identifier=None,
    )


def test_charfield_with_max_length_none_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(max_length=None)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_multiple_charfields_some_missing_max_length():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField()
    label = models.CharField(max_length=None)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 2  # noqa: PLR2004
    assert occurrences[0].line_number == 3  # noqa: PLR2004
    assert occurrences[1].line_number == 4  # noqa: PLR2004


def test_direct_charfield_import_found():
    source_tree = ast.parse("""from django.db.models import CharField


class MyModel(Model):
    name = CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 5  # noqa: PLR2004


def test_bare_charfield_without_models_import_ok():
    """Without an import from "django.db.models", a bare "CharField()" is some other class entirely."""
    source_tree = ast.parse("""from wtforms.fields import CharField


class MyForm(Form):
    name = CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_charfield_in_model_with_unresolvable_base_found():
    """The base class lives in another file; the qualified "models.CharField" spelling proves the field."""
    source_tree = ast.parse("""class Invoice(CommonInfo):
    reference = models.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_fully_qualified_charfield_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = django.db.models.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_aliased_models_module_charfield_found():
    source_tree = ast.parse("""from django.db import models as db_models


class MyModel(db_models.Model):
    name = db_models.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 5  # noqa: PLR2004


def test_output_field_charfield_ok():
    """A "CharField" typing a query expression creates no column, so "max_length" is meaningless there."""
    source_tree = ast.parse("""value = Cast("name", output_field=models.CharField())""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_charfield_with_kwargs_spread_ok():
    """A "**kwargs" spread may carry max_length; what cannot be seen is not flagged."""
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(**field_kwargs)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_charfield_with_other_kwargs_but_no_max_length_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(blank=True, null=True)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_charfield_with_other_kwargs_and_valid_max_length_ok():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(blank=True, max_length=255)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_charfield_with_valid_max_length_ok():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(max_length=255)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_textfield_ok():
    source_tree = ast.parse("""class MyModel(models.Model):
    description = models.TextField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_form_charfield_ok():
    source_tree = ast.parse("""class MyForm(forms.Form):
    name = forms.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_serializer_charfield_ok():
    source_tree = ast.parse("""class MySerializer(serializers.Serializer):
    name = serializers.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []


def test_model_charfield_in_non_model_class_found():
    """ "models.CharField()" is a model field wherever it is written, and still needs a "max_length"."""
    source_tree = ast.parse("""class MyForm(forms.Form):
    name = models.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_charfield_outside_class_found():
    source_tree = ast.parse("""name = models.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 1


def test_annotated_charfield_without_max_length_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    name: str = models.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_annotated_charfield_with_valid_max_length_ok():
    source_tree = ast.parse("""class MyModel(models.Model):
    name: str = models.CharField(max_length=255)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_annotated_charfield_with_max_length_none_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    name: str = models.CharField(max_length=None)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_bare_annotation_without_value_not_detected():
    source_tree = ast.parse("""class MyModel(models.Model):
    name: str""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_method_in_model_class_not_detected():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_charfield_with_max_length_none_before_kwargs_spread_found():
    """An explicit "max_length=None" settles it, whichever side of the spread it sits on."""
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(max_length=None, **field_kwargs)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_charfield_with_max_length_none_after_kwargs_spread_found():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(**field_kwargs, max_length=None)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


def test_charfield_with_valid_max_length_after_kwargs_spread_ok():
    source_tree = ast.parse("""class MyModel(models.Model):
    name = models.CharField(**field_kwargs, max_length=100)""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert occurrences == []
