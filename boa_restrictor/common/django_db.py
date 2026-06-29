import ast

from boa_restrictor.common.ast_utils import is_type_checking_if


def _imports_django_db(node) -> bool:
    """Returns whether the given import node imports "django.db" (or one of its submodules)."""
    if isinstance(node, ast.Import):
        return any(alias.name.startswith("django.db") for alias in node.names)
    return (node.module and node.module.startswith("django.db")) or (
        node.module == "django" and any(alias.name == "db" for alias in node.names)
    )


def find_django_db_import_line_numbers(source_tree: ast.AST) -> list[int]:
    """
    Returns the line numbers of all imports of "django.db" (or its submodules). Imports that only exist for
    type-checking purposes (inside an "if TYPE_CHECKING" block) are excluded since they don't create a runtime
    dependency on the database layer.
    """
    type_checking_lines = set()
    imports = []

    for node in ast.walk(source_tree):
        if is_type_checking_if(node):
            type_checking_lines.update(
                subnode.lineno
                for inner in node.body
                for subnode in ast.walk(inner)
                if isinstance(subnode, (ast.Import, ast.ImportFrom))
            )
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)

    return [node.lineno for node in imports if node.lineno not in type_checking_lines and _imports_django_db(node)]
