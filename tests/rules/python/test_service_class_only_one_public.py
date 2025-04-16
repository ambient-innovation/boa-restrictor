import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.python.service_class_only_one_public import ServiceClassHasOnlyOnePublicMethodRule


def test_functions_named_service_are_ignored():
    source_tree = ast.parse("""def myFunctionService():
            pass""")

    occurrences = ServiceClassHasOnlyOnePublicMethodRule.run_check(
        file_path=Path("my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_classes_not_named_service_are_ignored():
    source_tree = ast.parse("""class BeerHeuristics:
            pass""")

    occurrences = ServiceClassHasOnlyOnePublicMethodRule.run_check(
        file_path=Path("my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_service_class_missing_public_method():
    source_tree = ast.parse("""class MyService:
            pass""")

    occurrences = ServiceClassHasOnlyOnePublicMethodRule.run_check(
        file_path=Path("my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=1,
        rule_id=ServiceClassHasOnlyOnePublicMethodRule.RULE_ID,
        rule_label=ServiceClassHasOnlyOnePublicMethodRule.RULE_LABEL,
        identifier="MyService",
    )


def test_service_class_with_public_process_method():
    source_tree = ast.parse("""class MyService:
            def process():
                pass""")

    occurrences = ServiceClassHasOnlyOnePublicMethodRule.run_check(
        file_path=Path("my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 0


def test_service_class_with_protected_method():
    source_tree = ast.parse("""class MyService:
            def _process():
                pass""")

    occurrences = ServiceClassHasOnlyOnePublicMethodRule.run_check(
        file_path=Path("my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=1,
        rule_id=ServiceClassHasOnlyOnePublicMethodRule.RULE_ID,
        rule_label=ServiceClassHasOnlyOnePublicMethodRule.RULE_LABEL,
        identifier="MyService",
    )


def test_service_class_with_multiple_public_methods():
    source_tree = ast.parse("""class MyService:
            def durp():
                pass

            def process():
                pass""")

    occurrences = ServiceClassHasOnlyOnePublicMethodRule.run_check(
        file_path=Path("my_file.py"), source_tree=source_tree
    )

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=1,
        rule_id=ServiceClassHasOnlyOnePublicMethodRule.RULE_ID,
        rule_label=ServiceClassHasOnlyOnePublicMethodRule.RULE_LABEL,
        identifier="MyService",
    )
