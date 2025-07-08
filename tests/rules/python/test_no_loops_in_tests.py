import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import NoLoopsInTestsRule


def test_pytest_for_loop_is_detected():
    source_tree = ast.parse("""def test_something():
    for i in list:
        pass""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/tests/test_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_file.py",
        file_path=Path("/path/to/tests/test_file.py"),
        line_number=1,
        rule_id=NoLoopsInTestsRule.RULE_ID,
        rule_label=NoLoopsInTestsRule.RULE_LABEL,
        identifier="test_something",
    )


def test_pytest_while_loop_is_detected():
    source_tree = ast.parse("""def test_something():
    while i < 0:
        pass""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/tests/test_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_file.py",
        file_path=Path("/path/to/tests/test_file.py"),
        line_number=1,
        rule_id=NoLoopsInTestsRule.RULE_ID,
        rule_label=NoLoopsInTestsRule.RULE_LABEL,
        identifier="test_something",
    )


def test_pytest_list_comprehension_loop_is_detected():
    source_tree = ast.parse("""def test_something():
    numbers = [1, 2, 3, 4, 5]
    squared_numbers = [x * x for x in numbers]""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/tests/test_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_file.py",
        file_path=Path("/path/to/tests/test_file.py"),
        line_number=1,
        rule_id=NoLoopsInTestsRule.RULE_ID,
        rule_label=NoLoopsInTestsRule.RULE_LABEL,
        identifier="test_something",
    )


def test_pytest_nested_loop_is_detected():
    source_tree = ast.parse("""def test_something():
    if len(list) > 0:
        for i in list:
            pass""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/tests/test_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_file.py",
        file_path=Path("/path/to/tests/test_file.py"),
        line_number=1,
        rule_id=NoLoopsInTestsRule.RULE_ID,
        rule_label=NoLoopsInTestsRule.RULE_LABEL,
        identifier="test_something",
    )


def test_pytest_no_loop_is_detected():
    source_tree = ast.parse("""def test_something():
    if len(list) > 0:
        pass""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/tests/test_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_unittest_for_loop_is_detected():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_something(self):
        for i in list:
            pass""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/tests/test_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_file.py",
        file_path=Path("/path/to/tests/test_file.py"),
        line_number=2,
        rule_id=NoLoopsInTestsRule.RULE_ID,
        rule_label=NoLoopsInTestsRule.RULE_LABEL,
        identifier="test_something",
    )


def test_unittest_while_loop_is_detected():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_something():
        while i < 0:
            pass""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/tests/test_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_file.py",
        file_path=Path("/path/to/tests/test_file.py"),
        line_number=2,
        rule_id=NoLoopsInTestsRule.RULE_ID,
        rule_label=NoLoopsInTestsRule.RULE_LABEL,
        identifier="test_something",
    )


def test_unittest_loop_is_detected_from_non_test_case_class():
    source_tree = ast.parse("""class MyTestCase(InheritedTestCase):
    def test_something():
        while i < 0:
            pass""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/tests/test_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_file.py",
        file_path=Path("/path/to/tests/test_file.py"),
        line_number=2,
        rule_id=NoLoopsInTestsRule.RULE_ID,
        rule_label=NoLoopsInTestsRule.RULE_LABEL,
        identifier="test_something",
    )


def test_loops_ok_in_non_test_dir():
    source_tree = ast.parse("""def test_something():
    while i < 0:
        pass""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/code/test_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_loops_ok_in_non_test_file():
    source_tree = ast.parse("""def test_something():
    while i < 0:
        pass""")

    occurrences = NoLoopsInTestsRule.run_check(file_path=Path("/path/to/tests/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_is_test_file_test_file_in_test_dir():
    assert NoLoopsInTestsRule._is_test_file(filepath=Path("path/to/tests/test_file.py")) is True


def test_is_test_file_test_file_but_not_test_dir():
    assert NoLoopsInTestsRule._is_test_file(filepath=Path("path/to/code/test_file.py")) is False


def test_is_test_file_no_test_file_in_test_dir():
    assert NoLoopsInTestsRule._is_test_file(filepath=Path("path/to/tests/mixins.py")) is False


def test_is_test_file_test_file_in_test_dir_but_not_py():
    assert NoLoopsInTestsRule._is_test_file(filepath=Path("path/to/tests/test_file.md")) is False
