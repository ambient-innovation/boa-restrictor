import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import NoDjangoDbImportInApiRule


def test_check_deep_import():
    source_tree = ast.parse("""from django.db.models.functions import Concat""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/file/api.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="api.py",
        file_path=Path("/path/to/file/api.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInApiRule.RULE_ID,
        rule_label=NoDjangoDbImportInApiRule.RULE_LABEL,
        identifier=None,
    )


def test_check_models_import():
    source_tree = ast.parse("""from django.db import models""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/file/api.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="api.py",
        file_path=Path("/path/to/file/api.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInApiRule.RULE_ID,
        rule_label=NoDjangoDbImportInApiRule.RULE_LABEL,
        identifier=None,
    )


def test_check_db_import():
    source_tree = ast.parse("""from django import db""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/file/api.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="api.py",
        file_path=Path("/path/to/file/api.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInApiRule.RULE_ID,
        rule_label=NoDjangoDbImportInApiRule.RULE_LABEL,
        identifier=None,
    )


def test_check_full_import():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/file/api.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="api.py",
        file_path=Path("/path/to/file/api.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInApiRule.RULE_ID,
        rule_label=NoDjangoDbImportInApiRule.RULE_LABEL,
        identifier=None,
    )


def test_check_view_module():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/api/user.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="user.py",
        file_path=Path("/path/to/api/user.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInApiRule.RULE_ID,
        rule_label=NoDjangoDbImportInApiRule.RULE_LABEL,
        identifier=None,
    )


def test_check_no_api_file():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("managers.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_migrations_are_ok():
    source_tree = ast.parse("""import django.db.models.functions.comparison""")

    occurrences = NoDjangoDbImportInApiRule.run_check(
        file_path=Path("migrations/0001_initial.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_check_no_db_import_import():
    source_tree = ast.parse("""import django.conf.settings""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/file/api.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_no_db_form_import():
    source_tree = ast.parse("""from django.conf import settings""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/file/api.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_typing_type_hinting_imports_are_excluded():
    source_tree = ast.parse("""if typing.TYPE_CHECKING:
    from django.db import QuerySet""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/file/api.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_constant_type_hinting_imports_are_excluded():
    source_tree = ast.parse("""if TYPE_CHECKING:
    from django.db import QuerySet""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/file/api.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_other_ifs_are_ignored():
    source_tree = ast.parse("""if a == 1:
    from django.db import QuerySet""")

    occurrences = NoDjangoDbImportInApiRule.run_check(file_path=Path("/path/to/file/api.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="api.py",
        file_path=Path("/path/to/file/api.py"),
        line_number=2,
        rule_id=NoDjangoDbImportInApiRule.RULE_ID,
        rule_label=NoDjangoDbImportInApiRule.RULE_LABEL,
        identifier=None,
    )
