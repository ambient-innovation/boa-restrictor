import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.django.prohibit_assert_raises import AssertRaisesProhibitedRule


def test_check_occurrence_duplication_no_duplication():
    rule = AssertRaisesProhibitedRule(file_path=Path("my_file.py"), source_tree=ast.parse("a=1"))

    assert rule._check_occurrence_duplication(occurrences=[], filename="my_file.py", line_number=7) is False


def test_check_occurrence_duplication_no_duplication_via_file():
    rule = AssertRaisesProhibitedRule(file_path=Path("my_file.py"), source_tree=ast.parse("a=1"))
    occurrence = Occurrence(
        line_number=7,
        filename="my_file.py",
        rule_id=AssertRaisesProhibitedRule.RULE_ID,
        rule_label=AssertRaisesProhibitedRule.RULE_LABEL,
        identifier=None,
    )
    assert rule._check_occurrence_duplication(occurrences=[occurrence], filename="my_file.py", line_number=1) is False


def test_check_occurrence_duplication_no_duplication_via_line_no():
    rule = AssertRaisesProhibitedRule(file_path=Path("my_file.py"), source_tree=ast.parse("a=1"))
    occurrence = Occurrence(
        line_number=1,
        filename="other_file.py",
        rule_id=AssertRaisesProhibitedRule.RULE_ID,
        rule_label=AssertRaisesProhibitedRule.RULE_LABEL,
        identifier=None,
    )
    assert rule._check_occurrence_duplication(occurrences=[occurrence], filename="my_file.py", line_number=1) is False


def test_check_occurrence_duplication_has_duplication():
    rule = AssertRaisesProhibitedRule(file_path=Path("my_file.py"), source_tree=ast.parse("a=1"))

    occurrence = Occurrence(
        line_number=7,
        filename="my_file.py",
        rule_id=AssertRaisesProhibitedRule.RULE_ID,
        rule_label=AssertRaisesProhibitedRule.RULE_LABEL,
        identifier=None,
    )
    assert rule._check_occurrence_duplication(occurrences=[occurrence], filename="my_file.py", line_number=7) is True


def test_check_direct_call_false():
    rule = AssertRaisesProhibitedRule(file_path=Path("my_file.py"), source_tree=ast.parse("a=1"))

    code = "some_other_object.assertRaises(ValueError, func)"
    tree = ast.parse(code)
    node = tree.body[0].value

    assert rule._check_direct_call(node=node) is False


def test_check_context_manager_call_not_a_call():
    rule = AssertRaisesProhibitedRule(file_path=Path("my_file.py"), source_tree=ast.parse("a=1"))

    code = """with obj.some_method as value:
         my_function()
     """
    tree = ast.parse(code)
    node = tree.body[0]

    assert rule._check_context_manager(node=node) is False


def test_check_context_manager_call_other_object():
    rule = AssertRaisesProhibitedRule(file_path=Path("my_file.py"), source_tree=ast.parse("a=1"))

    code = """with some_object.assertRaises(ValueError):
        my_function()
     """
    tree = ast.parse(code)
    node = tree.body[0]

    assert rule._check_context_manager(node=node) is False


def test_assert_raises_in_context_manager():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_my_test(self):
        with self.assertRaises(RuntimeError):
            my_function()""")

    occurrences = AssertRaisesProhibitedRule.run_check(file_path=Path("my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=3,
        rule_id=AssertRaisesProhibitedRule.RULE_ID,
        rule_label=AssertRaisesProhibitedRule.RULE_LABEL,
        identifier=None,
    )


def test_assert_raises_direct_usage():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_my_test(self):
        self.assertRaises(RuntimeError)""")

    occurrences = AssertRaisesProhibitedRule.run_check(file_path=Path("my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=3,
        rule_id=AssertRaisesProhibitedRule.RULE_ID,
        rule_label=AssertRaisesProhibitedRule.RULE_LABEL,
        identifier=None,
    )


def test_assert_raises_message_used():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_my_test(self):
        with self.assertRaisesMessage(RuntimeError, "Hola mundo!"):
            my_function()""")

    occurrences = AssertRaisesProhibitedRule.run_check(file_path=Path("my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0
