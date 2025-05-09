import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import AvoidTypeHintsInVariableNamesAsSuffix


def test_check_variable_ends_on_list():
    source_tree = ast.parse("""user_list = []""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AvoidTypeHintsInVariableNamesAsSuffix.RULE_ID,
        rule_label=AvoidTypeHintsInVariableNamesAsSuffix.RULE_LABEL,
        identifier="user_list",
    )


def test_check_variable_ends_on_dict():
    source_tree = ast.parse("""user_dict = {}""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AvoidTypeHintsInVariableNamesAsSuffix.RULE_ID,
        rule_label=AvoidTypeHintsInVariableNamesAsSuffix.RULE_LABEL,
        identifier="user_dict",
    )


def test_check_variable_ends_on_set():
    source_tree = ast.parse("""user_set = ()""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AvoidTypeHintsInVariableNamesAsSuffix.RULE_ID,
        rule_label=AvoidTypeHintsInVariableNamesAsSuffix.RULE_LABEL,
        identifier="user_set",
    )


def test_check_variable_ends_on_str():
    source_tree = ast.parse("""user_str = ''""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AvoidTypeHintsInVariableNamesAsSuffix.RULE_ID,
        rule_label=AvoidTypeHintsInVariableNamesAsSuffix.RULE_LABEL,
        identifier="user_str",
    )


def test_check_variable_ends_on_int():
    source_tree = ast.parse("""user_int = 0""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AvoidTypeHintsInVariableNamesAsSuffix.RULE_ID,
        rule_label=AvoidTypeHintsInVariableNamesAsSuffix.RULE_LABEL,
        identifier="user_int",
    )


def test_check_variable_ends_on_float():
    source_tree = ast.parse("""user_float = 0.0""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AvoidTypeHintsInVariableNamesAsSuffix.RULE_ID,
        rule_label=AvoidTypeHintsInVariableNamesAsSuffix.RULE_LABEL,
        identifier="user_float",
    )


def test_check_variable_ends_on_bool():
    source_tree = ast.parse("""user_bool = False""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AvoidTypeHintsInVariableNamesAsSuffix.RULE_ID,
        rule_label=AvoidTypeHintsInVariableNamesAsSuffix.RULE_LABEL,
        identifier="user_bool",
    )


def test_check_variable_ends_on_qs():
    source_tree = ast.parse("""user_qs = UserQuerySet()""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AvoidTypeHintsInVariableNamesAsSuffix.RULE_ID,
        rule_label=AvoidTypeHintsInVariableNamesAsSuffix.RULE_LABEL,
        identifier="user_qs",
    )


def test_check_annotated_variable_ends_on_blocklisted_suffix():
    source_tree = ast.parse("""user_list: list = []""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        file_path=Path("/path/to/file/my_file.py"),
        line_number=1,
        rule_id=AvoidTypeHintsInVariableNamesAsSuffix.RULE_ID,
        rule_label=AvoidTypeHintsInVariableNamesAsSuffix.RULE_LABEL,
        identifier="user_list",
    )


def test_check_annotated_variable_unpacking():
    source_tree = ast.parse("""my_dict[key]: str = 'value'""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_check_variable_no_specific_ending():
    source_tree = ast.parse("""users = []""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_check_variable_unpacking():
    source_tree = ast.parse("""a, b = [1, 2]""")

    occurrences = AvoidTypeHintsInVariableNamesAsSuffix.run_check(
        file_path=Path("/path/to/file/my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0
