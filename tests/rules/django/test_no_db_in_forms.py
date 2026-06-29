import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import NoDjangoDbImportInFormsRule


def test_check_deep_import():
    source_tree = ast.parse("""from django.db.models.functions import Concat""")

    occurrences = NoDjangoDbImportInFormsRule.run_check(
        file_path=Path("/path/to/file/forms.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="forms.py",
        file_path=Path("/path/to/file/forms.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInFormsRule.RULE_ID,
        rule_label=NoDjangoDbImportInFormsRule.RULE_LABEL,
        identifier=None,
    )


def test_check_models_import():
    source_tree = ast.parse("""from django.db import models""")

    occurrences = NoDjangoDbImportInFormsRule.run_check(
        file_path=Path("/path/to/file/forms.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1


def test_check_forms_module():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInFormsRule.run_check(
        file_path=Path("/path/to/forms/user.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="user.py",
        file_path=Path("/path/to/forms/user.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInFormsRule.RULE_ID,
        rule_label=NoDjangoDbImportInFormsRule.RULE_LABEL,
        identifier=None,
    )


def test_check_no_form_file():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInFormsRule.run_check(file_path=Path("managers.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_no_db_import():
    source_tree = ast.parse("""from django.conf import settings""")

    occurrences = NoDjangoDbImportInFormsRule.run_check(
        file_path=Path("/path/to/file/forms.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_check_typing_type_hinting_imports_are_excluded():
    source_tree = ast.parse("""if TYPE_CHECKING:
    from django.db import QuerySet""")

    occurrences = NoDjangoDbImportInFormsRule.run_check(
        file_path=Path("/path/to/file/forms.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0
