import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.python.asterisk_required import AsteriskRequiredRule


def test_method_has_asterisk():
    source_tree = ast.parse("""class MyClass:
        def my_method(self, *, a):
            pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_method_no_params():
    source_tree = ast.parse("""class MyClass:
        def my_method(self):
            pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_method_missing_asterisk():
    source_tree = ast.parse("""class MyClass:
        def my_method(self, a):
            pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=2,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        identifier="my_method",
    )


def test_function_has_asterisk():
    source_tree = ast.parse("""def my_function(*, a):
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_function_no_params():
    source_tree = ast.parse("""def my_function():
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_function_missing_asterisk():
    source_tree = ast.parse("""def my_function(a):
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        identifier="my_function",
    )


def test_function_asterisk_too_late():
    source_tree = ast.parse("""def my_function(a, *, b):
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        identifier="my_function",
    )


def test_function_arg_with_defaults():
    source_tree = ast.parse("""def my_function(a=42):
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        identifier="my_function",
    )


def test_async_function_has_asterisk():
    source_tree = ast.parse("""async def my_function(*, a):
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_async_function_missing_asterisk():
    source_tree = ast.parse("""async def my_function(a):
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        identifier="my_function",
    )


def test_self_outside_of_class_not_matched():
    source_tree = ast.parse("""def my_function(self):
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_cls_outside_of_class_not_matched():
    source_tree = ast.parse("""def my_function(cls):
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0


def test_leading_cls_and_following_attributes():
    source_tree = ast.parse("""def my_function(cls, a):
        pass
    """)

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        identifier="my_function",
    )


def test_lambda_not_matched():
    source_tree = ast.parse("""double = lambda x: x * 2""")

    occurrences = AsteriskRequiredRule.run_check(file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree)

    assert len(occurrences) == 0
