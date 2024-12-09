import ast

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.dataclass_kw_only import DataclassWithKwargsOnlyRule


def test_dataclass_kw_only_set():
    source_tree = ast.parse("""import dataclass
@dataclasses.dataclass(kw_only=True)
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0


def test_dataclass_kw_only_missing():
    source_tree = ast.parse("""import dataclass
@dataclasses.dataclass
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=3,
        rule_id=DataclassWithKwargsOnlyRule.RULE_ID,
        rule_label=DataclassWithKwargsOnlyRule.RULE_LABEL,
        function_name=None,
    )


def test_dataclass_kw_only_set_but_false():
    source_tree = ast.parse("""import dataclass
@dataclasses.dataclass(kw_only=False)
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=3,
        rule_id=DataclassWithKwargsOnlyRule.RULE_ID,
        rule_label=DataclassWithKwargsOnlyRule.RULE_LABEL,
        function_name=None,
    )


def test_nested_import_kwargs_set():
    source_tree = ast.parse("""from dataclasses import dataclass
@dataclass(kw_only=True)
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0


def test_nested_import_kwargs_missing():
    source_tree = ast.parse("""from dataclasses import dataclass
@dataclass
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=3,
        rule_id=DataclassWithKwargsOnlyRule.RULE_ID,
        rule_label=DataclassWithKwargsOnlyRule.RULE_LABEL,
        function_name=None,
    )


def test_nested_import_kwargs_set_but_false():
    source_tree = ast.parse("""from dataclasses import dataclass
@dataclass(kw_only=False)
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=3,
        rule_id=DataclassWithKwargsOnlyRule.RULE_ID,
        rule_label=DataclassWithKwargsOnlyRule.RULE_LABEL,
        function_name=None,
    )
