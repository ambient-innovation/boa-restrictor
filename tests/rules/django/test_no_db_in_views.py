import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import NoDjangoDbImportInViewsRule


def test_check_deep_import():
    source_tree = ast.parse("""from django.db.models.functions import Concat""")

    occurrences = NoDjangoDbImportInViewsRule.run_check(file_path=Path("views.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="views.py",
        line_number=1,
        rule_id=NoDjangoDbImportInViewsRule.RULE_ID,
        rule_label=NoDjangoDbImportInViewsRule.RULE_LABEL,
        identifier=None,
    )


def test_check_models_import():
    source_tree = ast.parse("""from django.db import models""")

    occurrences = NoDjangoDbImportInViewsRule.run_check(file_path=Path("views.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="views.py",
        line_number=1,
        rule_id=NoDjangoDbImportInViewsRule.RULE_ID,
        rule_label=NoDjangoDbImportInViewsRule.RULE_LABEL,
        identifier=None,
    )


def test_check_db_import():
    source_tree = ast.parse("""from django import db""")

    occurrences = NoDjangoDbImportInViewsRule.run_check(file_path=Path("views.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="views.py",
        line_number=1,
        rule_id=NoDjangoDbImportInViewsRule.RULE_ID,
        rule_label=NoDjangoDbImportInViewsRule.RULE_LABEL,
        identifier=None,
    )


def test_check_full_import():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInViewsRule.run_check(file_path=Path("views.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="views.py",
        line_number=1,
        rule_id=NoDjangoDbImportInViewsRule.RULE_ID,
        rule_label=NoDjangoDbImportInViewsRule.RULE_LABEL,
        identifier=None,
    )


def test_check_view_module():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInViewsRule.run_check(
        file_path=Path("/path/to/views/user.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="user.py",
        line_number=1,
        rule_id=NoDjangoDbImportInViewsRule.RULE_ID,
        rule_label=NoDjangoDbImportInViewsRule.RULE_LABEL,
        identifier=None,
    )


def test_check_no_views_file():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInViewsRule.run_check(file_path=Path("managers.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_migrations_are_ok():
    source_tree = ast.parse("""import django.db.models.functions.comparison""")

    occurrences = NoDjangoDbImportInViewsRule.run_check(
        file_path=Path("migrations/0001_initial.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0
