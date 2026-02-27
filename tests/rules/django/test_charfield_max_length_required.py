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
    source_tree = ast.parse("""class MyModel(Model):
    name = CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].line_number == 2  # noqa: PLR2004


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


def test_non_model_class_not_detected():
    source_tree = ast.parse("""class MyForm(forms.Form):
    name = models.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_charfield_outside_class_not_detected():
    source_tree = ast.parse("""name = models.CharField()""")

    occurrences = CharFieldMaxLengthRequiredRule.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0
