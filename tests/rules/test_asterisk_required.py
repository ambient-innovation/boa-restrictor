from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.asterisk_required import AsteriskRequiredRule


def test_method_has_asterisk():
    source_code = """class MyClass:
        def my_method(self, *, a):
            pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 0


def test_method_no_params():
    source_code = """class MyClass:
        def my_method(self):
            pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 0


def test_method_missing_asterisk():
    source_code = """class MyClass:
        def my_method(self, a):
            pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=2,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        function_name="my_method",
    )


def test_function_has_asterisk():
    source_code = """def my_function(*, a):
        pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 0


def test_function_no_params():
    source_code = """def my_function():
        pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 0


def test_function_missing_asterisk():
    source_code = """def my_function(a):
        pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=1,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        function_name="my_function",
    )


def test_function_asterisk_too_late():
    source_code = """def my_function(a, *, b):
        pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=1,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        function_name="my_function",
    )


def test_async_function_has_asterisk():
    source_code = """async def my_function(*, a):
        pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 0


def test_async_function_missing_asterisk():
    source_code = """async def my_function(a):
        pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=1,
        rule_id=AsteriskRequiredRule.RULE_ID,
        rule_label=AsteriskRequiredRule.RULE_LABEL,
        function_name="my_function",
    )


def test_self_outside_of_class_not_matched():
    source_code = """def my_function(self):
        pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 0


def test_cls_outside_of_class_not_matched():
    source_code = """def my_function(cls):
        pass
    """

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 0


def test_lambda_not_matched():
    source_code = """double = lambda x: x * 2"""

    rule = AsteriskRequiredRule(filename="my_file.py", source_code=source_code)
    occurrences = rule.check(source_code=source_code)

    assert len(occurrences) == 0