import argparse
import os
import sys
from unittest import mock

from boa_restrictor.cli.main import main
from boa_restrictor.common.rule import Rule
from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules import AsteriskRequiredRule, ReturnStatementRequiresTypeHintRule


@mock.patch.object(argparse.ArgumentParser, "parse_args")
def test_main_arguments_parsed(mocked_parse_args):
    main(
        argv=(
            "boa-restrictor",
            os.path.abspath(sys.argv[0]),
            "--config",
            "pyproject.toml",
        )
    )

    mocked_parse_args.assert_called_once_with(
        ("boa-restrictor", os.path.abspath(sys.argv[0]), "--config", "pyproject.toml"),
    )


@mock.patch("boa_restrictor.cli.main.load_configuration", return_value={"exclude": ["PBR001"]})
@mock.patch.object(ReturnStatementRequiresTypeHintRule, "run_check")
@mock.patch.object(AsteriskRequiredRule, "run_check")
def test_main_exclude_config_active(mocked_run_checks_asterisk, mocked_run_checks_return_type, *args):
    main(
        argv=(
            "boa-restrictor",
            os.path.abspath(sys.argv[0]),
            "--config",
            "pyproject.toml",
        )
    )

    mocked_run_checks_asterisk.assert_not_called()
    mocked_run_checks_return_type.assert_called_once()


@mock.patch("boa_restrictor.cli.main.get_noqa_comments", return_value=[])
def test_main_noqa_comments_called(mocked_get_noqa_comments):
    main(
        argv=(
            "boa-restrictor",
            os.path.abspath(sys.argv[0]),
            "--config",
            "pyproject.toml",
        )
    )

    mocked_get_noqa_comments.assert_called_once()


@mock.patch.object(sys.stdout, "write")
def test_main_occurrences_are_written_to_cli(mocked_write):
    occurrence = Occurrence(
        rule_id="PBR000",
        rule_label="One to rule them all.",
        filename="my_file.py",
        line_number=42,
        function_name="my_function",
    )

    with mock.patch.object(
        Rule,
        "run_check",
        return_value=[occurrence],
    ) as mocked_run_checks:
        main(
            argv=(
                "boa-restrictor",
                os.path.abspath(sys.argv[0]),
                "--config",
                "pyproject.toml",
            )
        )

    # We have more than one rule
    assert mocked_run_checks.call_count > 1

    # We expect one line per occurrence and one final summary
    assert mocked_write.call_count == mocked_run_checks.call_count + 1
