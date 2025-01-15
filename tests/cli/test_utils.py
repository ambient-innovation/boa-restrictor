import ast

import pytest

from boa_restrictor.cli.utils import parse_source_code_or_fail
from boa_restrictor.exceptions.syntax_errors import BoaRestrictorParsingError


def test_parse_source_code_or_fail_valid_code():
    result = parse_source_code_or_fail(filename="my_file.py", source_code="a = 1")

    assert isinstance(result, ast.Module)


def test_parse_source_code_or_fail_invalid_code():
    with pytest.raises(BoaRestrictorParsingError, match='Source code of file "my_file.py" contains syntax errors.'):
        parse_source_code_or_fail(filename="my_file.py", source_code="""f\"asf""")
