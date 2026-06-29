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


def test_directly_imported_field_without_related_name_is_detected():
    source_tree = ast.parse("""class Book(models.Model):
    author = ForeignKey(Author, on_delete=CASCADE)""")

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2, identifier="ForeignKey")]


def test_call_with_non_name_callable_is_ignored():
    source_tree = ast.parse("""class Book(models.Model):
    author = field_factory()(Author)""")

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


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


def test_meta_default_related_name_is_ok():
    source_tree = ast.parse(
        """class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        default_related_name = "books\""""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_meta_default_related_name_as_annotated_assignment_is_ok():
    source_tree = ast.parse(
        """class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        default_related_name: str = "books\""""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_meta_default_related_name_exempts_only_its_own_model():
    source_tree = ast.parse(
        """class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        default_related_name = "books"


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=9, identifier="ForeignKey")]


def test_meta_without_default_related_name_still_flags():
    source_tree = ast.parse(
        """class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        ordering = ("id",)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2, identifier="ForeignKey")]


def test_default_related_name_inherited_from_abstract_base_in_same_file_is_ok():
    source_tree = ast.parse(
        """class CommonInfo(models.Model):
    class Meta:
        abstract = True
        default_related_name = "books"


class Book(CommonInfo):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_default_related_name_inherited_transitively_is_ok():
    source_tree = ast.parse(
        """class Base(models.Model):
    class Meta:
        abstract = True
        default_related_name = "books"


class Intermediate(Base):
    pass


class Book(Intermediate):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_meta_subclassing_base_meta_with_default_related_name_is_ok():
    source_tree = ast.parse(
        """class CommonInfo(models.Model):
    class Meta:
        abstract = True
        default_related_name = "books"


class Book(CommonInfo):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta(CommonInfo.Meta):
        ordering = ("id",)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_own_meta_not_extending_base_meta_does_not_inherit_default_related_name():
    source_tree = ast.parse(
        """class CommonInfo(models.Model):
    class Meta:
        abstract = True
        default_related_name = "books"


class Book(CommonInfo):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        ordering = ("id",)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=8, identifier="ForeignKey")]


def test_base_without_default_related_name_still_flags():
    source_tree = ast.parse(
        """class CommonInfo(models.Model):
    class Meta:
        abstract = True
        ordering = ("id",)


class Book(CommonInfo):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=8, identifier="ForeignKey")]


def test_meta_subclassing_standalone_base_meta_by_name_is_ok():
    # "class Meta(BaseMeta)" referencing a standalone Meta base by its bare name inherits its options.
    source_tree = ast.parse(
        """class BaseMeta:
    default_related_name = "books"


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta(BaseMeta):
        ordering = ("id",)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_meta_extending_base_meta_without_default_related_name_still_flags():
    # "class Meta(Other.Meta)" where the parent Meta has no default_related_name does not exempt the model.
    source_tree = ast.parse(
        """class Other(models.Model):
    class Meta:
        ordering = ("id",)


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta(Other.Meta):
        ordering = ("id",)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=7, identifier="ForeignKey")]


def test_meta_with_non_assignment_statement_still_flags():
    # A Meta body statement that is neither an assignment nor an annotated assignment is skipped harmlessly.
    source_tree = ast.parse(
        """class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        pass"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2, identifier="ForeignKey")]


def test_meta_subclassing_standalone_base_meta_without_default_related_name_still_flags():
    # A standalone base Meta that does not set default_related_name does not exempt the model.
    source_tree = ast.parse(
        """class BaseMeta:
    ordering = ("id",)


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta(BaseMeta):
        pass"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=6, identifier="ForeignKey")]


def test_meta_subclassing_base_meta_from_other_file_cannot_be_resolved_and_flags():
    # The base Meta lives in another module, so the linter cannot see its options and (conservatively) flags.
    source_tree = ast.parse(
        """class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta(ImportedBaseMeta):
        pass"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2, identifier="ForeignKey")]


def test_field_declared_on_base_model_is_flagged_on_the_base():
    # A relation field is checked where it is declared (the base), not re-checked on subclasses.
    source_tree = ast.parse(
        """class CommonInfo(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Book(CommonInfo):
    title = models.CharField(max_length=100)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2, identifier="ForeignKey")]


def test_inheritance_from_base_in_other_file_cannot_be_resolved_and_flags():
    # The base lives in another module, so the linter cannot see its Meta and (conservatively) flags.
    source_tree = ast.parse(
        """class Book(TimeStampedModel):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)"""
    )

    occurrences = RelatedNameRequiredRule.run_check(file_path=MODELS_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2, identifier="ForeignKey")]


def test_migration_file_is_ignored():
    source_tree = ast.parse("""author = models.ForeignKey(Author, on_delete=models.CASCADE)""")

    occurrences = RelatedNameRequiredRule.run_check(
        file_path=Path("/path/to/app/migrations/0001_initial.py"), source_tree=source_tree
    )

    assert occurrences == []
