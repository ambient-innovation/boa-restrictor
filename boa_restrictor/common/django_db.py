import ast
from _ast import AST


def is_type_checking_if(node) -> bool:
    """
    Returns whether the given node is an "if TYPE_CHECKING:" (or "if typing.TYPE_CHECKING:") block.
    """
    if isinstance(node, ast.If):
        test = node.test
        # Case 1: TYPE_CHECKING
        if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
            return True
        # Case 2: typing.TYPE_CHECKING
        elif (
            isinstance(test, ast.Attribute)
            and isinstance(test.value, ast.Name)
            and test.value.id == "typing"
            and test.attr == "TYPE_CHECKING"
        ):
            return True
    return False


def find_django_db_import_line_numbers(source_tree: AST) -> list[int]:  # noqa: C901
    """
    Returns the line numbers of all imports of "django.db" (or its submodules). Imports that only exist for
    type-checking purposes (inside an "if TYPE_CHECKING" block) are excluded since they don't create a runtime
    dependency on the database layer.
    """
    line_numbers = []
    type_checking_lines = set()
    pending_imports = []

    # Single walk: collect type-checking line numbers and pending imports simultaneously
    for node in ast.walk(source_tree):
        if is_type_checking_if(node):
            for inner in node.body:
                for subnode in ast.walk(inner):
                    if isinstance(subnode, (ast.Import, ast.ImportFrom)):
                        type_checking_lines.add(subnode.lineno)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            pending_imports.append(node)

    for node in pending_imports:
        if node.lineno in type_checking_lines:
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("django.db"):
                    line_numbers.append(node.lineno)
        elif (node.module and node.module.startswith("django.db")) or (
            node.module == "django" and any(alias.name == "db" for alias in node.names)
        ):
            line_numbers.append(node.lineno)

    return line_numbers
