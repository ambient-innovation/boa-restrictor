import ast


def node_name(node) -> str | None:
    """
    Returns the bare name of an AST node: the id of an "ast.Name" or the attr of an "ast.Attribute".
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


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
