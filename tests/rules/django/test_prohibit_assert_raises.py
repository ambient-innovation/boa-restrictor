import ast

from boa_restrictor.rules.django.prohibit_assert_raises import AssertRaisesProhibitedRule


def test_assert_raises_in_context_manager():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_my_test(self):
        with self.assertRaises(RuntimeError):
            my_function()""")

    occurrences = AssertRaisesProhibitedRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 1


def test_assert_raises_direct_usage():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_my_test(self):
        self.assertRaises(RuntimeError)""")

    occurrences = AssertRaisesProhibitedRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 1


def test_assert_raises_message_used():
    source_tree = ast.parse("""class MyTestCase(TestCase):
    def test_my_test(self):
        with self.assertRaisesMessage(RuntimeError, "Hola mundo!"):
            my_function()""")

    occurrences = AssertRaisesProhibitedRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0
