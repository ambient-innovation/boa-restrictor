from unittest import mock

import pytest

from boa_restrictor.common.rule import Rule


@mock.patch.object(Rule, "check")
def test_run_check(mocked_check):
    Rule.run_check(filename="my/file.py", source_code="Python!")

    mocked_check.assert_called_with(source_code="Python!")


def test_init_variables_set():
    rule = Rule(filename="my/file.py", source_code="Python!")

    assert rule.filename == "my/file.py"
    assert rule.source_code == "Python!"


def test_check_not_implemented():
    with pytest.raises(NotImplementedError):
        Rule.run_check(filename="my/file.py", source_code="Python!")
