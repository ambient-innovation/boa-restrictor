import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import NoInlineImportInTestsRule

TEST_FILE_PATH = Path("/path/to/tests/test_file.py")


def _occurrence(line_number: int) -> Occurrence:
    return Occurrence(
        filename="test_file.py",
        file_path=TEST_FILE_PATH,
        line_number=line_number,
        rule_id=NoInlineImportInTestsRule.RULE_ID,
        rule_label=NoInlineImportInTestsRule.RULE_LABEL,
        identifier=None,
    )


def test_inline_import_is_detected():
    source_tree = ast.parse("""def test_something():
    import os
    assert os""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2)]


def test_inline_import_from_is_detected():
    source_tree = ast.parse("""def test_something():
    from os import path
    assert path""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2)]


def test_inline_import_in_method_is_detected():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_something(self):
        from os import path
        assert path""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=3)]


def test_inline_import_in_nested_function_is_detected():
    source_tree = ast.parse("""def test_something():
    def helper():
        import os
        return os""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=3)]


def test_module_level_import_is_ok():
    source_tree = ast.parse("""import os


def test_something():
    assert os""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_inline_import_in_non_test_file_is_ok():
    source_tree = ast.parse("""def some_function():
    import os
    return os""")

    occurrences = NoInlineImportInTestsRule.run_check(
        file_path=Path("/path/to/code/helpers.py"), source_tree=source_tree
    )

    assert occurrences == []


def test_inline_type_checking_import_in_function_is_ok():
    source_tree = ast.parse("""def test_something():
    if TYPE_CHECKING:
        from os import path
    assert path""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_inline_qualified_type_checking_import_in_function_is_ok():
    source_tree = ast.parse("""def test_something():
    if typing.TYPE_CHECKING:
        from os import path
    assert path""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_module_level_type_checking_import_is_ok():
    source_tree = ast.parse("""if TYPE_CHECKING:
    from os import path


def test_something():
    assert path""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_import_in_else_branch_of_type_checking_guard_is_detected():
    source_tree = ast.parse("""def test_something():
    if TYPE_CHECKING:
        from os import path
    else:
        import os
    assert os and path""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=5)]


def test_import_in_else_branch_at_module_level_is_ok():
    source_tree = ast.parse("""if TYPE_CHECKING:
    from os import path
else:
    import os
""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_inline_import_in_compound_guard_is_detected():
    source_tree = ast.parse("""def test_something():
    if a == b:
        import os
    assert os""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=3)]


def test_inline_import_in_non_type_checking_guard_is_detected():
    source_tree = ast.parse("""def test_something():
    if some_condition:
        import os
    assert os""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=3)]


def test_multiple_inline_imports_are_detected():
    source_tree = ast.parse("""def test_something():
    import os
    from sys import argv
    assert os and argv""")

    occurrences = NoInlineImportInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2), _occurrence(line_number=3)]
