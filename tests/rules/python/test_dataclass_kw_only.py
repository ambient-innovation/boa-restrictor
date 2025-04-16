import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.python.dataclass_kw_only import DataclassWithKwargsOnlyRule


def test_dataclass_kw_only_set():
    source_tree = ast.parse("""import dataclass
@dataclasses.dataclass(kw_only=True)
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_other_class_decorator():
    source_tree = ast.parse("""
@abc.ABCMeta.register
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_dataclass_kw_only_missing():
    source_tree = ast.parse("""import dataclass
@dataclasses.dataclass
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=3,
        rule_id=DataclassWithKwargsOnlyRule.RULE_ID,
        rule_label=DataclassWithKwargsOnlyRule.RULE_LABEL,
        identifier=None,
    )


def test_dataclass_kw_only_set_but_false():
    source_tree = ast.parse("""import dataclass
@dataclasses.dataclass(kw_only=False)
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=3,
        rule_id=DataclassWithKwargsOnlyRule.RULE_ID,
        rule_label=DataclassWithKwargsOnlyRule.RULE_LABEL,
        identifier=None,
    )


def test_nested_import_kwargs_set():
    source_tree = ast.parse("""from dataclasses import dataclass
@dataclass(kw_only=True)
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_nested_import_kwargs_missing():
    source_tree = ast.parse("""from dataclasses import dataclass
@dataclass
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=3,
        rule_id=DataclassWithKwargsOnlyRule.RULE_ID,
        rule_label=DataclassWithKwargsOnlyRule.RULE_LABEL,
        identifier=None,
    )


def test_nested_import_kwargs_set_but_false():
    source_tree = ast.parse("""from dataclasses import dataclass
@dataclass(kw_only=False)
class MyDataclass:
    pass""")

    occurrences = DataclassWithKwargsOnlyRule.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=3,
        rule_id=DataclassWithKwargsOnlyRule.RULE_ID,
        rule_label=DataclassWithKwargsOnlyRule.RULE_LABEL,
        identifier=None,
    )
