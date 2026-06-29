import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import ServiceClassNameRule

SERVICE_FILE_PATH = Path("/path/to/file/services.py")


def _occurrence(*, line_number: int, identifier: str) -> Occurrence:
    return Occurrence(
        filename="services.py",
        file_path=SERVICE_FILE_PATH,
        line_number=line_number,
        rule_id=ServiceClassNameRule.RULE_ID,
        rule_label=ServiceClassNameRule.RULE_LABEL,
        identifier=identifier,
    )


def test_service_suffix_is_ok():
    source_tree = ast.parse("""class CreateUserService:
    def process(self): ...""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_missing_suffix_is_detected():
    source_tree = ast.parse("""class CreateUser:
    def process(self): ...""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=1, identifier="CreateUser")]


def test_missing_suffix_in_services_dir_is_detected():
    source_tree = ast.parse("""class CreateUser: ...""")

    occurrences = ServiceClassNameRule.run_check(file_path=Path("/path/to/services/user.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0].identifier == "CreateUser"


def test_exception_class_is_ok():
    source_tree = ast.parse("""class UserNotFoundError(Exception): ...""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_enum_class_is_ok():
    source_tree = ast.parse("""class Color(Enum):
    RED = 1""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_dataclass_is_ok():
    source_tree = ast.parse("""@dataclass
class UserData:
    name: str""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_typed_dict_is_ok():
    source_tree = ast.parse("""class UserPayload(TypedDict):
    name: str""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_nested_class_is_ignored():
    source_tree = ast.parse("""class CreateUserService:
    class Meta:
        verbose_name = "x" """)

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_top_level_non_class_node_is_ignored():
    source_tree = ast.parse("""def create_user():
    ...

CONSTANT = 42""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_dataclass_call_form_is_ok():
    source_tree = ast.parse("""@dataclass(frozen=True)
class UserData:
    name: str""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_dotted_dataclass_decorator_is_ok():
    source_tree = ast.parse("""@dataclasses.dataclass
class UserData:
    name: str""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_dotted_enum_base_is_ok():
    source_tree = ast.parse("""class Color(enum.Enum):
    RED = 1""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == []


def test_subscripted_base_is_detected():
    source_tree = ast.parse("""class CreateUser(Generic[T]): ...""")

    occurrences = ServiceClassNameRule.run_check(file_path=SERVICE_FILE_PATH, source_tree=source_tree)

    assert occurrences == [_occurrence(line_number=1, identifier="CreateUser")]


def test_non_service_file_is_ok():
    source_tree = ast.parse("""class CreateUser: ...""")

    occurrences = ServiceClassNameRule.run_check(file_path=Path("/path/to/file/managers.py"), source_tree=source_tree)

    assert occurrences == []
