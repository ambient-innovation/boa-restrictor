import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import NoObjectsCreateInTestsRule

TEST_FILE_PATH = Path("/path/to/tests/test_file.py")


def _occurrence(line_number: int) -> Occurrence:
    return Occurrence(
        filename="test_file.py",
        file_path=TEST_FILE_PATH,
        line_number=line_number,
        rule_id=NoObjectsCreateInTestsRule.RULE_ID,
        rule_label=NoObjectsCreateInTestsRule.RULE_LABEL,
        identifier=None,
    )


def test_objects_create_is_detected():
    source_tree = ast.parse("""def test_something():
    user = User.objects.create(name="Ron")
    assert user""")

    occurrences = NoObjectsCreateInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2)]


def test_objects_create_on_dotted_path_is_detected():
    source_tree = ast.parse("""def test_something():
    user = myapp.models.User.objects.create(name="Ron")
    assert user""")

    occurrences = NoObjectsCreateInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=2)]


def test_objects_filter_is_ok():
    source_tree = ast.parse("""def test_something():
    qs = User.objects.filter(name="Ron")
    assert qs""")

    occurrences = NoObjectsCreateInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_baker_make_is_ok():
    source_tree = ast.parse("""def test_something():
    user = baker.make(User)
    assert user""")

    occurrences = NoObjectsCreateInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_unrelated_create_is_ok():
    source_tree = ast.parse("""def test_something():
    obj = factory.create(name="Ron")
    assert obj""")

    occurrences = NoObjectsCreateInTestsRule.run_check(file_path=TEST_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_objects_create_in_non_test_file_is_ok():
    source_tree = ast.parse("""def setup():
    return User.objects.create(name="Ron")""")

    occurrences = NoObjectsCreateInTestsRule.run_check(
        file_path=Path("/path/to/services/user.py"), source_tree=source_tree
    )

    assert occurrences == []
