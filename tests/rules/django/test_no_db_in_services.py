import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import NoDjangoDbImportInServicesRule


def test_check_deep_import():
    source_tree = ast.parse("""from django.db.models.functions import Concat""")

    occurrences = NoDjangoDbImportInServicesRule.run_check(
        file_path=Path("/path/to/file/services.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="services.py",
        file_path=Path("/path/to/file/services.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInServicesRule.RULE_ID,
        rule_label=NoDjangoDbImportInServicesRule.RULE_LABEL,
        identifier=None,
    )


def test_check_models_import():
    source_tree = ast.parse("""from django.db import models""")

    occurrences = NoDjangoDbImportInServicesRule.run_check(
        file_path=Path("/path/to/file/services.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="services.py",
        file_path=Path("/path/to/file/services.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInServicesRule.RULE_ID,
        rule_label=NoDjangoDbImportInServicesRule.RULE_LABEL,
        identifier=None,
    )


def test_check_full_import():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInServicesRule.run_check(
        file_path=Path("/path/to/file/services.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1


def test_check_services_module():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInServicesRule.run_check(
        file_path=Path("/path/to/services/user.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="user.py",
        file_path=Path("/path/to/services/user.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInServicesRule.RULE_ID,
        rule_label=NoDjangoDbImportInServicesRule.RULE_LABEL,
        identifier=None,
    )


def test_check_no_service_file():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInServicesRule.run_check(file_path=Path("managers.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_no_db_import():
    source_tree = ast.parse("""from django.conf import settings""")

    occurrences = NoDjangoDbImportInServicesRule.run_check(
        file_path=Path("/path/to/file/services.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_check_typing_type_hinting_imports_are_excluded():
    source_tree = ast.parse("""if TYPE_CHECKING:
    from django.db import QuerySet""")

    occurrences = NoDjangoDbImportInServicesRule.run_check(
        file_path=Path("/path/to/file/services.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0
