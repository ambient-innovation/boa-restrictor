import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from pathlib import Path
from unittest import mock

from boa_restrictor.cli.configuration import load_configuration

EXISTING_FILE = Path.cwd().parent.parent / "pyproject.toml"


@mock.patch.object(tomllib, "load", return_value={"tool": {"boa-restrictor": {"exclude": ["PBR001"]}}})
def test_load_configuration_happy_path(mocked_load):
    assert os.path.isfile(EXISTING_FILE)

    data = load_configuration(file_path=EXISTING_FILE)

    mocked_load.assert_called_once()
    assert data == {"exclude": ["PBR001"]}


@mock.patch.object(tomllib, "load")
def test_load_configuration_invalid_file(mocked_load):
    data = load_configuration(file_path="invalid_file.toml")

    mocked_load.assert_not_called()
    assert data == {}


@mock.patch.object(tomllib, "load", return_value={"tool": {"other_linter": True}})
def test_load_configuration_key_missing(mocked_load):
    data = load_configuration(file_path=EXISTING_FILE)

    mocked_load.assert_called_once()
    assert data == {}
