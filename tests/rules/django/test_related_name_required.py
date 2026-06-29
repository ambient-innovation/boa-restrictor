import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import RelatedNameRequiredRule

MODELS_FILE_PATH = Path("/path/to/app/models.py")


def _occurrence(*, line_number: int, identifier: str) -> Occurrence:
    return Occurrence(
        filename="models.py",
        file_path=MODELS_FILE_PATH,
        line_number=line_number,
        rule_id=RelatedNameRequiredRule.RULE_ID,
        rule_label=RelatedNameRequiredRule.RULE_LABEL,
        identifier=identifier,
    )


def test_foreign_key_without_related_name_is_detected():
    source_tree = ast.parse("""class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)""")

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2, identifier="ForeignKey")]


def test_foreign_key_with_related_name_is_ok():
    source_tree = ast.parse(
        """class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_disabled_reverse_relation_is_ok():
    source_tree = ast.parse(
        """class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="+")"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_one_to_one_field_without_related_name_is_detected():
    source_tree = ast.parse("""class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)""")

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2, identifier="OneToOneField")]


def test_many_to_many_field_without_related_name_is_detected():
    source_tree = ast.parse("""class Book(models.Model):
    tags = models.ManyToManyField(Tag)""")

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2, identifier="ManyToManyField")]


def test_non_relational_field_is_ok():
    source_tree = ast.parse("""class Book(models.Model):
    title = models.CharField(max_length=100)""")

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_kwargs_spread_is_ignored():
    source_tree = ast.parse("""class Book(models.Model):
    author = models.ForeignKey(Author, **field_kwargs)""")

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_migration_file_is_ignored():
    source_tree = ast.parse("""author = models.ForeignKey(Author, on_delete=models.CASCADE)""")

    occurrences = RelatedNameRequiredRule.run_check(
        file_path=Path("/path/to/app/migrations/0001_initial.py"), source_tree=source_tree
    )

    assert occurrences == []
