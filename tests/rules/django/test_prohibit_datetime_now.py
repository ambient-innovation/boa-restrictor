import ast
from pathlib import Path

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.django.prohibit_datetime_now import ProhibitDatetimeNow


def test_datetime_now_import_found():
    source_tree = ast.parse("""from datetime import datetime
timestamp = datetime.now()""")

    occurrences = ProhibitDatetimeNow.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="file.py",
        file_path=Path("/path/to/file.py"),
        line_number=2,
        rule_id=ProhibitDatetimeNow.RULE_ID,
        rule_label=ProhibitDatetimeNow.RULE_LABEL,
        identifier=None,
    )


def test_direct_import_found():
    source_tree = ast.parse("""import datetime
timestamp = datetime.datetime.now()""")

    occurrences = ProhibitDatetimeNow.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="file.py",
        file_path=Path("/path/to/file.py"),
        line_number=2,
        rule_id=ProhibitDatetimeNow.RULE_ID,
        rule_label=ProhibitDatetimeNow.RULE_LABEL,
        identifier=None,
    )


def test_sub_import_found():
    source_tree = ast.parse("""from datetime.datetime import now
timestamp = now()""")

    occurrences = ProhibitDatetimeNow.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="file.py",
        file_path=Path("/path/to/file.py"),
        line_number=2,
        rule_id=ProhibitDatetimeNow.RULE_ID,
        rule_label=ProhibitDatetimeNow.RULE_LABEL,
        identifier=None,
    )


def test_renamed_import_found():
    source_tree = ast.parse("""from datetime import datetime as dt
timestamp = dt.now()""")

    occurrences = ProhibitDatetimeNow.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="file.py",
        file_path=Path("/path/to/file.py"),
        line_number=2,
        rule_id=ProhibitDatetimeNow.RULE_ID,
        rule_label=ProhibitDatetimeNow.RULE_LABEL,
        identifier=None,
    )


def test_other_datetime_import_not_found():
    source_tree = ast.parse("""from datetime import datetime
timestamp = datetime.today()""")

    occurrences = ProhibitDatetimeNow.run_check(file_path=Path("/path/to/file.py"), source_tree=source_tree)

    assert len(occurrences) == 0
