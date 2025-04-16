import ast
from pathlib import Path
from unittest import mock

import pytest

from boa_restrictor.common.rule import Rule


@mock.patch.object(Rule, "check")
def test_run_check(mocked_check):
    Rule.run_check(file_path=Path("my/file.py"), source_tree=ast.parse("a=1"))

    mocked_check.assert_called_with()
    mocked_check.assert_called_once()


def test_init_variables_set():
    parsed_source_code = ast.parse("a=1")
    rule = Rule(file_path=Path("my/file.py"), source_tree=parsed_source_code)

    assert rule.file_path == Path("my/file.py")
    assert rule.filename == "file.py"
    assert rule.source_tree == parsed_source_code


def test_check_not_implemented():
    with pytest.raises(NotImplementedError):
        Rule.run_check(file_path=Path("my/file.py"), source_tree=ast.parse("a=1"))
