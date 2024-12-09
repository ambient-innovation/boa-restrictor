import ast

from boa_restrictor.projections.occurrence import Occurrence
from boa_restrictor.rules.global_import_datetime import GlobalImportDatetimeRule


def test_global_import_datetime():
    source_tree = ast.parse("""import datetime
my_date = datetime.datetime(2024, 9, 19)
    """)

    occurrences = GlobalImportDatetimeRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 0


def test_nested_import_datetime():
    source_tree = ast.parse("""from datetime import datetime
my_datetime = datetime(2024, 9, 19)
    """)

    occurrences = GlobalImportDatetimeRule.run_check(filename="my_file.py", source_tree=source_tree)

    assert len(occurrences) == 1
    assert occurrences[0] == Occurrence(
        filename="my_file.py",
        line_number=1,
        rule_id=GlobalImportDatetimeRule.RULE_ID,
        rule_label=GlobalImportDatetimeRule.RULE_LABEL,
        function_name=None,
    )
