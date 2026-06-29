import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import MandatoryTestAssertionRule

TEST_FILE_PATH = Path("/path/to/tests/test_file.py")


def _occurrence(*, line_number: int, identifier: str) -> Occurrence:
    return Occurrence(
        filename="test_file.py",
        file_path=TEST_FILE_PATH,
        line_number=line_number,
        rule_id=MandatoryTestAssertionRule.RULE_ID,
        rule_label=MandatoryTestAssertionRule.RULE_LABEL,
        identifier=identifier,
    )


def test_bare_assert_is_ok():
    source_tree = ast.parse("""def test_something():
    assert True""")

    occurrences = MandatoryTestAssertionRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_unittest_assert_method_is_ok():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_something(self):
        self.assertEqual(1, 1)""")

    occurrences = MandatoryTestAssertionRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_pytest_raises_is_ok():
    source_tree = ast.parse("""def test_something():
    with pytest.raises(ValueError):
        do_something()""")

    occurrences = MandatoryTestAssertionRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_assert_raises_context_manager_is_ok():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_something(self):
        with self.assertRaises(ValueError):
            do_something()""")

    occurrences = MandatoryTestAssertionRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_assertion_nested_in_block_is_ok():
    source_tree = ast.parse("""def test_something():
    if condition:
        assert True""")

    occurrences = MandatoryTestAssertionRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_missing_assertion_is_detected():
    source_tree = ast.parse("""def test_something():
    result = do_something()
    print(result)""")

    occurrences = MandatoryTestAssertionRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=1, identifier="test_something")]


def test_missing_assertion_in_async_test_is_detected():
    source_tree = ast.parse("""async def test_something():
    await do_something()""")

    occurrences = MandatoryTestAssertionRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=1, identifier="test_something")]


def test_non_test_function_is_ignored():
    source_tree = ast.parse("""def helper():
    return do_something()""")

    occurrences = MandatoryTestAssertionRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_missing_assertion_in_non_test_file_is_ok():
    source_tree = ast.parse("""def test_something():
    do_something()""")

    occurrences = MandatoryTestAssertionRule.run_check(
        file_path=Path("/path/to/code/helpers.py"), source_tree=source_tree
    )

    assert occurrences == []
