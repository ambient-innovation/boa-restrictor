import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import NoDjangoDbImportInTasksRule


def test_check_deep_import():
    source_tree = ast.parse("""from django.db.models.functions import Concat""")

    occurrences = NoDjangoDbImportInTasksRule.run_check(
        file_path=Path("/path/to/file/tasks.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="tasks.py",
        file_path=Path("/path/to/file/tasks.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInTasksRule.RULE_ID,
        rule_label=NoDjangoDbImportInTasksRule.RULE_LABEL,
        identifier=None,
    )


def test_check_models_import():
    source_tree = ast.parse("""from django.db import models""")

    occurrences = NoDjangoDbImportInTasksRule.run_check(
        file_path=Path("/path/to/file/tasks.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1


def test_check_tasks_module():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInTasksRule.run_check(
        file_path=Path("/path/to/tasks/cleanup.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="cleanup.py",
        file_path=Path("/path/to/tasks/cleanup.py"),
        line_number=1,
        rule_id=NoDjangoDbImportInTasksRule.RULE_ID,
        rule_label=NoDjangoDbImportInTasksRule.RULE_LABEL,
        identifier=None,
    )


def test_check_no_task_file():
    source_tree = ast.parse("""import django.db.models""")

    occurrences = NoDjangoDbImportInTasksRule.run_check(file_path=Path("managers.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_no_db_import():
    source_tree = ast.parse("""from django.conf import settings""")

    occurrences = NoDjangoDbImportInTasksRule.run_check(
        file_path=Path("/path/to/file/tasks.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_check_typing_type_hinting_imports_are_excluded():
    source_tree = ast.parse("""if TYPE_CHECKING:
    from django.db import QuerySet""")

    occurrences = NoDjangoDbImportInTasksRule.run_check(
        file_path=Path("/path/to/file/tasks.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0
