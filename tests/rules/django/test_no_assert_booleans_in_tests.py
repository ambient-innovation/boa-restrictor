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
        line_number=1,
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
        line_number=1,
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
        line_number=1,
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


def test_check_assert_in_different_class():
    source_tree = ast.parse("""class MyTest(Service):
    def test_x(self):
        self.assertTrue(x)""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_assert_in_different_class_indirect_import():
    source_tree = ast.parse("""class MyTest(my_app.Service):
    def test_x(self):
        self.assertTrue(x)""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_check_assert_with_class_variable():
    source_tree = ast.parse("""class MyTest(TestCase):
    something = 123""")

    occurrences = ProhibitAssertBooleanInTests.run_check(file_path=Path("test_x.py"), source_tree=source_tree)

    assert len(occurrences) == 0
