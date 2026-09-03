import ast
from typing import TypeGuard


def node_name(node) -> str | None:
    """
    Returns the bare name of an AST node: the id of an "ast.Name" or the attr of an "ast.Attribute".
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def index_classes_by_name(source_tree: ast.AST) -> dict[str, ast.ClassDef]:
    """
    Indexes every class in the given tree by its name, so a base class can be resolved as far as one file
    allows. A name declared more than once resolves to the last definition, which is what the interpreter
    would bind it to.
    """
    return {node.name: node for node in ast.walk(source_tree) if isinstance(node, ast.ClassDef)}


def resolve_class(node, classes_by_name: dict[str, ast.ClassDef]) -> ast.ClassDef | None:
    """
    Returns the class the given base expression refers to, or None when it is defined in another file.
    """
    name = node_name(node)
    return classes_by_name.get(name) if name is not None else None


def is_test_function(node) -> TypeGuard[ast.FunctionDef | ast.AsyncFunctionDef]:
    """
    Returns whether the given AST node is a test function: a (sync or async) function whose name starts with
    "test" and which is NOT a pytest fixture. pytest does not collect fixtures as tests even when they are
    named "test_*" (e.g. a "test_client" fixture), so they must not be treated as tests.
    """
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    if not node.name.startswith("test"):
        return False
    return not is_fixture(node)


def is_fixture(node) -> bool:
    """
    Returns whether the given AST node is a function decorated as a pytest fixture, i.e. carrying a
    "@pytest.fixture", "@pytest.fixture(...)" or (directly-imported) "@fixture" / "@fixture(...)" decorator.
    """
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    for decorator in node.decorator_list:
        # Unwrap parametrized decorators ("@pytest.fixture(...)" / "@fixture(...)") to their callee, so both
        # "@pytest.fixture" and "@pytest.fixture(scope="module")" (and the directly-imported "@fixture") match.
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if node_name(target) == "fixture":
            return True
    return False


def is_type_checking_if(node) -> bool:
    """
    Returns whether the given node is an "if TYPE_CHECKING:" (or "if typing.TYPE_CHECKING:") block.
    """
    if not isinstance(node, ast.If):
        return False

    test = node.test
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute)
        and isinstance(test.value, ast.Name)
        and test.value.id == "typing"
        and test.attr == "TYPE_CHECKING"
    )
