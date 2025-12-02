import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.django.no_assert_booleans_in_tests import ProhibitAssertBooleanInTests


def test_check_assert_true_found():
    source_tree = ast.parse("""class MyTest(TestCase):
    def test_x(self):
        self.assertTrue(x)""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_x.py",
        file_path=Path("test_x.py"),
        line_number=3,
        rule_id=ProhibitAssertBooleanInTests.RULE_ID,
        rule_label=ProhibitAssertBooleanInTests.RULE_LABEL,
        identifier=None,
    )


def test_check_assert_false_found():
    source_tree = ast.parse("""class MyTest(TestCase):
    def test_x(self):
        self.assertFalse(x)""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_x.py",
        file_path=Path("test_x.py"),
        line_number=3,
        rule_id=ProhibitAssertBooleanInTests.RULE_ID,
        rule_label=ProhibitAssertBooleanInTests.RULE_LABEL,
        identifier=None,
    )


def test_check_assert_via_test_case_class_indirect_usage():
    source_tree = ast.parse("""class MyTest(tests.TestCase):
    def test_x(self):
        self.assertFalse(x)""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_x.py",
        file_path=Path("test_x.py"),
        line_number=3,
        rule_id=ProhibitAssertBooleanInTests.RULE_ID,
        rule_label=ProhibitAssertBooleanInTests.RULE_LABEL,
        identifier=None,
    )


def test_check_different_assert_not_found():
    source_tree = ast.parse("""class MyTest(TestCase):
    def test_x(self):
        self.assertIs(x, True)""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_assert_on_non_self_object():
    source_tree = ast.parse("""class MyTest(TestCase):
    def test_x(self):
        some_other_object.assertTrue(x)""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_assert_in_custom_testcase_subclass():
    """Verify the rule works with custom TestCase subclasses (not direct TestCase inheritance)."""
    source_tree = ast.parse("""class CustomTestCase(TestCase):
    pass

class MyTest(CustomTestCase):
    def test_x(self):
        self.assertTrue(x)""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="test_x.py",
        file_path=Path("test_x.py"),
        line_number=6,
        rule_id=ProhibitAssertBooleanInTests.RULE_ID,
        rule_label=ProhibitAssertBooleanInTests.RULE_LABEL,
        identifier=None,
    )


def test_check_assert_with_class_variable():
    source_tree = ast.parse("""class MyTest(TestCase):
    something = 123""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 0
