import ast

from boa_restrictor.exceptions.syntax_errors import BoaRestrictorParsingError


def parse_source_code_or_fail(*, filename: str, source_code: str) -> ast.Module:
    """
    Parse code through abstract syntax tree.
    Raise a human-readable error message if parsing fails.
    """
    try:
        return ast.parse(source_code)
    except SyntaxError as e:
        raise BoaRestrictorParsingError(filename=filename) from e
