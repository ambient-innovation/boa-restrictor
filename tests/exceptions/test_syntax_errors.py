import pytest

from boa_restrictor.exceptions.syntax_errors import BoaRestrictorParsingError


def test_parsing_error():
    exception = BoaRestrictorParsingError(filename="my_file")

    with pytest.raises(BoaRestrictorParsingError, match='Source code of file "my_file" contains syntax errors.'):
        raise exception
