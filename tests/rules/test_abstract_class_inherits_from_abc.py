import ast

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.abstract_class_inherits_from_abc import AbstractClassesInheritFromAbcRule


def test_functions_named_abstract_are_ignored():
    source_tree = ast.parse("""def abstract_function():
            pass""")

    occurrences = AbstractClassesInheritFromAbcRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0


def test_classes_not_named_abstract_are_ignored():
    source_tree = ast.parse("""class BeerHeuristics:
            pass""")

    occurrences = AbstractClassesInheritFromAbcRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0


def test_abstract_class_missing_abc_inheritance():
    source_tree = ast.parse("""class AbstractService:
            pass""")

    occurrences = AbstractClassesInheritFromAbcRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=1,
        rule_id=AbstractClassesInheritFromAbcRule.RULE_ID,
        rule_label=AbstractClassesInheritFromAbcRule.RULE_LABEL,
        identifier="AbstractService",
    )


def test_abstract_class_having_abc_inheritance():
    source_tree = ast.parse("""class AbstractService(abc.ABC):
            pass""")

    occurrences = AbstractClassesInheritFromAbcRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0


def test_abstract_class_having_direct_abc_inheritance():
    source_tree = ast.parse("""class AbstractService(ABC):
            pass""")

    occurrences = AbstractClassesInheritFromAbcRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0


def test_abstract_class_having_abc_and_other_inheritance():
    source_tree = ast.parse("""class AbstractService(MyMixin, abc.ABC):
            pass""")

    occurrences = AbstractClassesInheritFromAbcRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0


def test_abstract_class_via_metaclass():
    source_tree = ast.parse("""class MyAbstractMetaClass(metaclass=ABCMeta):
    pass""")

    occurrences = AbstractClassesInheritFromAbcRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0


def test_abstract_class_lower_case():
    source_tree = ast.parse("""class abstractService:
    pass""")

    occurrences = AbstractClassesInheritFromAbcRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=1,
        rule_id=AbstractClassesInheritFromAbcRule.RULE_ID,
        rule_label=AbstractClassesInheritFromAbcRule.RULE_LABEL,
        identifier="abstractService",
    )
