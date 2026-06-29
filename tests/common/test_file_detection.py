from pathlib import Path

from boa_restrictor.common.file_detection import is_test_file


def test_is_test_file_test_file_in_test_dir():
    assert is_test_file(Path("path/to/tests/test_file.py")) is True


def test_is_test_file_test_file_but_not_test_dir():
    assert is_test_file(Path("path/to/code/test_file.py")) is False


def test_is_test_file_no_test_file_in_test_dir():
    assert is_test_file(Path("path/to/tests/mixins.py")) is False


def test_is_test_file_test_file_in_test_dir_but_not_py():
    assert is_test_file(Path("path/to/tests/test_file.md")) is False
