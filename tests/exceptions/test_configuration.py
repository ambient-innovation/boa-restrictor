import pytest

from boa_restrictor.exceptions.configuration import TomlParsingError


def test_toml_syntax_error():
    exception = TomlParsingError(filename="my_file")

    with pytest.raises(TomlParsingError, match='TOML file "my_file" contains syntax errors.'):
        raise exception
